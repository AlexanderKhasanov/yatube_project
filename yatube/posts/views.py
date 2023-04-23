from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Post, Group
from .forms import PostForm
from .utils import get_page

NUMBER_DISPLAY_POSTS = 10

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    page_obj = get_page(request, post_list, NUMBER_DISPLAY_POSTS)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group.all()
    page_obj = get_page(request, post_list, NUMBER_DISPLAY_POSTS)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    page_obj = get_page(request, post_list, NUMBER_DISPLAY_POSTS)
    context = {
        'author': user,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
        'num_posts': post.author.posts.count(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            new_post = post_form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', new_post.author.get_username())
        return render(request, 'posts/create_post.html', {'form': post_form})
    post_form = PostForm()
    return render(request, 'posts/create_post.html', {'form': post_form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    context = {
        'post': post,
        'form': PostForm(instance=post),
        'is_edit': True
    }
    if request.method == 'POST':
        post_form = PostForm(request.POST, instance=post)
        if post_form.is_valid():
            post_form.save()
            return redirect('posts:post_detail', post_id)
        context['form'] = post_form
        return render(request, 'posts/create_post.html', context)
    return render(request, 'posts/create_post.html', context)
