from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .models import Post, Group
from .forms import PostForm

NUMBER_DISPLAY_POSTS = 10

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, NUMBER_DISPLAY_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group.all()
    paginator = Paginator(post_list, NUMBER_DISPLAY_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    paginator = Paginator(post_list, NUMBER_DISPLAY_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'username': username,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    all_user_posts = Post.objects.filter(author=post.author)
    num_author_posts = len(all_user_posts)
    context = {
        'post': post,
        'num_posts': num_author_posts,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            text = post_form.cleaned_data['text']
            group = post_form.cleaned_data['group']
            user = User.objects.get(username=request.user)
            Post.objects.create(author=user, text=text, group=group)
            print(user.get_username())
            return redirect('posts:profile', user.get_username())
        return render(request, 'posts/create_post.html', {'post': post_form})
    post_form = PostForm
    return render(request, 'posts/create_post.html', {'form': post_form})


def post_edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    context = {
        'post': post,
        'form': PostForm(instance=post),
        'is_edit': True
    }
    if request.method == 'POST':
        post_form = PostForm(request.POST, instance=post)
        print('start edit')
        if post_form.is_valid():
            post = post_form.save()
            print('edit post succes')
            return redirect('posts:post_detail', post_id)
        context['form'] = post_form
        return render(request, 'posts/create_post.html', context)
    return render(request, 'posts/create_post.html', context)
