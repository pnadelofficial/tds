from django import forms
from forum.models import Category

class CommentForm(forms.Form):
    author = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your Name"
        })
    )
    body = forms.CharField(widget=forms.Textarea(
        attrs={
            "class": "form-control",
            "placeholder": "Leave a comment!"
        })
    )

class PostForm(forms.Form):
    title = forms.CharField(
        max_length=255
    )
    author = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your Name"
        })
    )
    body = forms.CharField(widget=forms.Textarea(
        attrs={
            "class": "form-control",
            "placeholder": "Make a post!"
        })
    )
    categories = forms.ModelMultipleChoiceField(
        queryset = Category.objects.all(),
        widget = forms.CheckboxSelectMultiple
    )
    project_file = forms.FileField()