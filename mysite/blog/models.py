from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    """
    Custom manager for Post model that returns only published posts.

    This manager filters the queryset to include only posts with a 'PUBLISHED' status.
    """

    def get_queryset(self):
        """
        Override the default get_queryset method to filter for published posts only.

        Returns:
            QuerySet: Filtered queryset containing only published posts
        """
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    """
    Blog post model representing articles in the blog application.

    This model stores all information related to blog posts including title, content,
    author information, publication status, and timestamps. It includes functionality
    for tagging posts and retrieving absolute URLs.
    """

    class Status(models.TextChoices):
        """
        Enumeration of possible post statuses.

        Attributes:
            DRAFT: Represents a draft post not yet published
            PUBLISHED: Represents a published post visible to users
        """

        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date="publish")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT
    )

    tags = TaggableManager()
    # Model managers
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["-publish"]
        indexes = [
            models.Index(fields=["-publish"]),
        ]

    def __str__(self):
        """
        String representation of the Post object.

        Returns:
            str: The post title
        """
        return self.title

    def get_absolute_url(self):
        """
        Get the absolute URL for the post detail view.

        This method constructs the URL for accessing the post detail page
        using the post's publication date and slug.

        Returns:
            str: URL to access this specific post
        """
        return reverse(
            "blog:post_detail",
            args=[self.publish.year, self.publish.month, self.publish.day, self.slug],
        )


class Comment(models.Model):
    """
    Comment model for blog posts.

    This model represents user comments on blog posts, including the commenter's
    information, comment content, timestamps, and moderation status.
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["created"]
        indexes = [
            models.Index(fields=["created"]),
        ]

    def __str__(self):
        """
        String representation of the Comment object.

        Returns:
            str: A string indicating the comment author and the post it belongs to
        """
        return f"Comment by {self.name} on {self.post}"
