from django.shortcuts import render,redirect
from forum.models import Post, Comment
from forum.forms import CommentForm, PostForm
import json

# Create your views here.
def home_view(request):
    posts = Post.objects.all().order_by('-created_on')

    context = {
        "posts": posts,
    }
    return render(request, 'home.html', context)

def forum_index(request):
    posts = Post.objects.all().order_by('-created_on')
    context = {
        "posts": posts,
    }
    return render(request, "forum_index.html", context)

def forum_category(request, category):
    posts = Post.objects.filter(
        categories__name__contains=category
    ).order_by(
        '-created_on'
    )
    context = {
        "category": category,
        "posts": posts
    }
    return render(request, "forum_category.html", context)

def forum_detail(request, pk):
    post = Post.objects.get(pk=pk)
    # f = open(f'/home/tuftsdh/tds/tufts_digital_scholarship/tuftsdh{post.project_file.url}')
    f = open(f'.{post.project_file.url}')
    data = json.load(f)

    image = post.project_image.url

    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                author=form.cleaned_data["author"],
                body=form.cleaned_data["body"],
                post=post
            )
            comment.save()

    comments = Comment.objects.filter(post=post)
    context = {
        "post": post,
        "form" : form,
        "comments": comments,
        'data': data,
        'image': image
    }

    return render(request, "forum_detail.html", context)