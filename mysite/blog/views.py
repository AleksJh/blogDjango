from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

# from django.views.generic import ListView
from taggit.models import Tag

from .forms import CommentForm, EmailPostForm, SearchForm
from .models import Post


@require_POST
def post_comment(request, post_id):
    """
    Handle the submission of a new comment on a blog post.

    This view processes POST requests for adding comments to a specific blog post.
    It validates the comment form data, associates the comment with the post,
    and saves it to the database if valid.

    Args:
        request: The HTTP request object
        post_id: The ID of the post to comment on

    Returns:
        HttpResponse: Rendered template with post, form, and comment context
    """
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create Comment class object without saving it
        comment = form.save(commit=False)

        comment.post = post
        comment.save()
    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )


def post_share(request, post_id):
    """
    Handle sharing a blog post via email.

    This view allows users to share a blog post with others via email.
    It handles both GET requests (displaying the form) and POST requests
    (processing the form and sending the email).

    Args:
        request: The HTTP request object
        post_id: The ID of the post to share

    Returns:
        HttpResponse: Rendered template with post, form, and sent status context
    """
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )
            send_mail(subject, message, "lernagorc90@gmail.com", {cd["to"]})
            sent = True

    else:
        form = EmailPostForm()
    return render(
        request, "blog/post/share.html", {"post": post, "form": form, "sent": sent}
    )


# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = "posts"
#     paginate_by = 3
#     template_name = "blog/post/list.html"
#
#     def paginate_queryset(self, queryset, page_size):
#         """
#         Override the method to handle pagination errors manually.
#         """
#         paginator = Paginator(queryset, page_size)
#         page = self.request.GET.get("page", 1)
#
#         try:
#             page_obj = paginator.page(page)
#         except PageNotAnInteger:
#             page_obj = paginator.page(1)
#         except EmptyPage:
#             page_obj = paginator.page(paginator.num_pages)
#
#         is_paginated = paginator.num_pages > 1
#
#         return (paginator, page_obj, page_obj.object_list, is_paginated)


def post_list(request, tag_slug=None):
    """
    Display a paginated list of published blog posts.

    This view retrieves all published posts or filters them by tag if a tag_slug
    is provided. It implements pagination to display a limited number of posts per page.

    Args:
        request: The HTTP request object
        tag_slug: Optional slug of a tag to filter posts by

    Returns:
        HttpResponse: Rendered template with posts and tag context
    """
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, "blog/post/list.html", {"posts": posts, "tag": tag})


def post_detail(request, year, month, day, post):
    """
    Display the detailed view of a specific blog post.

    This view retrieves a specific post by its date and slug, along with its
    active comments and a list of similar posts based on shared tags.

    Args:
        request: The HTTP request object
        year: The year the post was published
        month: The month the post was published
        day: The day the post was published
        post: The slug of the post

    Returns:
        HttpResponse: Rendered template with post, comments, comment form,
         and similar posts
    """
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    # Retrieve active comments for this post
    comments = post.comments.filter(active=True)

    # Comment form for users to add new comments
    form = CommentForm()

    # Find similar posts based on shared tags
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish"
    )[
        :4
    ]  # Get top 4 similar posts

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


def post_search(request):
    """
    Search for blog posts based on user query.

    This view handles the search functionality for blog posts. It uses PostgreSQL's
    full-text search capabilities to search in post titles and bodies with different
    weights, ranking results by relevance.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered template with search form, query, and results
    """
    form = SearchForm()
    query = None
    results = []

    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            # Create weighted search vectors for title and body fields
            search_vector = SearchVector("title", weight="A") + SearchVector(
                "body", weight="B"
            )
            search_query = SearchQuery(query)
            # Annotate posts with search rank and filter by minimum rank threshold
            results = (
                Post.published.annotate(
                    search=search_vector, rank=SearchRank(search_vector, search_query)
                )
                .filter(rank__gte=0.3)  # Only include results with rank >= 0.3
                .order_by("-rank")  # Order by relevance (highest rank first)
            )

    return render(
        request,
        "blog/post/search.html",
        {"form": form, "query": query, "results": results},
    )
