from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Post, Group, Follow
from .forms import PostForm, CommentForm
from .utils import get_page

NUMBER_DISPLAY_POSTS = 10
CACHE_SECONDS = 20

User = get_user_model()


@cache_page(CACHE_SECONDS, key_prefix='index_page')
def index(request):
    """Отобразить главную страницу"""
    post_list = Post.objects.all()
    page_obj = get_page(request, post_list, NUMBER_DISPLAY_POSTS)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Отобразить все посты определенной группы"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group.all()
    page_obj = get_page(request, post_list, NUMBER_DISPLAY_POSTS)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Отобразить профиль пользователя"""
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    page_obj = get_page(request, post_list, NUMBER_DISPLAY_POSTS)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=user).exists()
    )
    context = {
        'author': user,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Вывести подробную информацию про пост"""
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
        'form': CommentForm(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создание поста"""
    if request.method == 'POST':
        post_form = PostForm(
            request.POST or None,
            files=request.FILES or None,
        )
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
    """Изменение поста"""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    context = {
        'post': post,
        'form': PostForm(
            files=request.FILES or None,
            instance=post),
        'is_edit': True
    }
    if request.method == 'POST':
        post_form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if post_form.is_valid():
            post_form.save()
            return redirect('posts:post_detail', post_id)
        context['form'] = post_form
        return render(request, 'posts/create_post.html', context)
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Добавиние комментария"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Получить посты авторов, на которых пользователь подписан"""
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page(request, post_list, NUMBER_DISPLAY_POSTS)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписка на автора"""
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user,
        author=author,
    )
    if not follow.exists() and author != request.user:
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Дизлайк, отписка от автора"""
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user,
        author=author,
    )
    if follow.exists():
        follow.delete()
    return redirect('posts:profile', username)
