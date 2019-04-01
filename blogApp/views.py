from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import PostForm
from .models import Post
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-created_date')
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnIntager:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
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
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
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
