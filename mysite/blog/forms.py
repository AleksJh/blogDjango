from django import forms

from .models import Comment


class EmailPostForm(forms.Form):
    """
    Form for sharing blog posts via email.

    This form collects information needed to share a blog post with someone
    via email, including sender and recipient information and optional comments.
    """

    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    """
    Form for submitting comments on blog posts.

    This form is based on the Comment model and allows users to submit
    comments on blog posts with their name, email, and comment text.
    """

    class Meta:
        model = Comment
        fields = ["name", "email", "body"]


class SearchForm(forms.Form):
    """
    Form for searching blog posts.

    This simple form provides a single field for users to enter search queries
    to find relevant blog posts.
    """

    query = forms.CharField()
