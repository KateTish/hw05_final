from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page
    }
    return render(
        request,
        'index.html',
        context
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page': page
    }
    return render(
        request,
        'group.html',
        context
    )


@login_required
def new_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    context = {
        'form': form
    }
    return render(
        request,
        'new_post.html',
        context
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    following_count = Follow.objects.filter(user=author).count()
    followers_count = Follow.objects.filter(author=author).count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'author': author,
        'posts': posts,
        'following': following,
        'following_count': following_count,
        'followers_count': followers_count,
        'page': page,
    }
    return render(
        request,
        'profile.html',
        context
    )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post.comments.all()
    following_count = Follow.objects.filter(user=author).count()
    followers_count = Follow.objects.filter(author=author).count()
    context = {
        'author': author,
        'post': post,
        'form': form,
        'comments': comments,
        'following_count': following_count,
        'followers_count': followers_count
    }
    return render(
        request,
        'post.html',
        context
    )


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect(
            'post',
            username=username,
            post_id=post_id
        )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user == post.author and form.is_valid():
        form.save()
        return redirect(
            'post',
            username=username,
            post_id=post_id
        )
    context = {
        'author': author,
        'post': post,
        'form': form,
    }
    return render(
        request,
        'new_post.html',
        context
    )


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(
        request,
        'misc/500.html',
        status=500
    )


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(
            'post',
            username=username,
            post_id=post_id
        )
    context = {
        'author': author,
        'post': post,
        'form': form
    }
    return render(
        request,
        'comments.html',
        context
    )


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'page': page
    }
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    follow_user = get_object_or_404(User, username=username)
    if request.user != follow_user:
        Follow.objects.get_or_create(
            user=request.user,
            author=follow_user
        )
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    unfollow_user = get_object_or_404(User, username=username)
    get_object_or_404(
        Follow,
        user=request.user,
        author=unfollow_user
    ).delete()
    return redirect('profile', username=username)
