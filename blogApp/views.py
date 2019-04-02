from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import PostForm
from .models import Post
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
from django.db.models import Q


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-created_date')
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(
            Q(title__search=query) |
            Q(text__search=query) |
            Q(author__search=query)
        ).distinct()
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'post_detail.html', {'post': post})


def post_new(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            messages.success(request, "Successfully Created")
            return redirect('post_detail', pk=post.pk)
        else:
            messages.error(request, "Creation Error")
    else:
        form = PostForm()
    return render(request, 'post_edit.html', {'form': form})


def post_edit(request, pk):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES or None, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            messages.success(request, "Item Saved")
            return redirect('post_detail', pk=post.pk)
        else:
            messages.success(request, "Saving Error")
    else:
        form = PostForm(instance=post)
    return render(request, 'post_edit.html', {'form': form})


def post_delete(request, pk):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    post = Post.objects.get(pk=pk)
    post.delete()
    messages.success(request, "Successfully Deleted")
    return redirect('post_list')


def registration(request):
    if request.method == "POST":
        form = {
            'login': request.POST["login"],
            'password': request.POST["password"],
            'email': request.POST["email"],
        }
        if form["login"] and form["password"]:
            if User.objects.filter(username=form["login"]).exists():
                form['errors'] = u"Пользователь с таким именем уже существует"
                return render(request, 'blog/registration.html', {'form': form})
            User.objects.create_user(form["login"], form["email"], form["password"])
            return redirect('post_list')
        else:
            form['errors'] = u"Не все поля заполнены"
            return render(request, 'registration.html', {'form': form})
    else:
        return render(request, 'registration.html', {})


def authorization(request):
    if request.method == "POST":
        form = {
            'login': request.POST["login"],
            'password': request.POST["password"],
        }
        if form["login"] and form["password"]:
            user = authenticate(username=form["login"], password=form["password"])
            if user is not None:
                login(request, user)
                return redirect('post_list')
            else:
                form['errors'] = u"Неверно введен логи или пароль"
                return render(request, 'authorization.html', {'form': form})
        else:
            form['errors'] = u"Не все поля заполнены"
            return render(request, 'authorization.html', {'form': form})
    else:
        return render(request, 'authorization.html', {})


def login_out(request):
    logout(request)
    return redirect('post_list')
