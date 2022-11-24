from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginate_queryset

POSTS_ON_PAGE = 10


def index(request):
    """Возвращает главную страницу приложения"""
    template = "posts/index.html"
    posts = Post.objects.select_related('author').select_related('group').all()
    page_obj = paginate_queryset(request, posts, POSTS_ON_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Принимает slug группы
    Возвращает страницу этого сообщества с последними ссобщениями
    """
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()
    page_obj = paginate_queryset(request, posts, POSTS_ON_PAGE)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Принимает username пользователя
    Возвращает страницу-профиль этого пользователя
    """
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=User.objects.get
                                          (username=username)).exists()
    user_object = get_object_or_404(User, username=username)
    user_posts = user_object.posts.select_related(
        'group').all().annotate(posts_count=Count('id'))
    page_obj = paginate_queryset(request, user_posts, POSTS_ON_PAGE)
    context = {
        'user_object': user_object,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Принимает post_id поста
    Возвращает страницу с деталями этого поста
    """
    post_object = get_object_or_404(Post.objects.select_related(
        'author').select_related('group'), id=post_id)
    is_author = False
    if request.user == post_object.author:
        is_author = True
    form = CommentForm(
        request.POST or None,
    )
    comments = post_object.comments.all()
    context = {
        'post_object': post_object,
        'is_author': is_author,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создание нового поста"""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {
        'form': form,
    }

    if request.method == 'POST':
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect(reverse('posts:profile',
                            kwargs={'username': request.user.username}))

        return render(request, 'posts/create_post.html', {'form': form})

    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Редактирование поста"""
    is_edit = True
    post_object = get_object_or_404(Post.objects.select_related(
        'author'), id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_object,
    )
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    if request.user == post_object.author:
        if request.method == 'POST':
            if form.is_valid():
                post_object.text = form.cleaned_data['text']
                post_object.group = form.cleaned_data['group']
                post_object.save()
                return redirect(reverse('posts:post_detail',
                                kwargs={'post_id': post_object.id}))

            return render(request, 'posts/create_post.html',
                          {'form': form, 'is_edit': is_edit})

        return render(request, 'posts/create_post.html', context)
    return redirect((reverse('posts:post_detail',
                     kwargs={'post_id': post_object.id})))


@login_required
def add_comment(request, post_id):
    """Добавление комментария к посту"""
    post = get_object_or_404(Post.objects.select_related(
        'author'), id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Возвращает страницу постов любимых авторов"""
    user_object = request.user
    authors = user_object.follower.all().values_list('author', flat=True)
    posts = Post.objects.select_related('author').select_related(
        'group').filter(author__id__in=authors)
    template = "posts/follow.html"
    page_obj = paginate_queryset(request, posts, POSTS_ON_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    if request.user.username == username:
        return redirect('posts:profile', username=username)
    author = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(user=request.user,
                                 author=author,
                                 )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора"""
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user,
                             author=author,
                             ).exists() is False:
        return redirect('posts:profile', username=username)
    Follow.objects.filter(user=request.user,
                          author=author).delete()
    return redirect('posts:profile', username=username)
