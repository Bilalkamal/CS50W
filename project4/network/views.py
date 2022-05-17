from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from .models import User, Post, Like, Follow


@login_required
@csrf_exempt
def get_all_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    posts = [post.serialize() for post in posts]
    # get the count of likes for each post
    posts = [{
        **post,
        'likes': len(Like.objects.filter(post=post['id']))
    } for post in posts]
    return JsonResponse(posts, safe=False)


@login_required
@csrf_exempt
def create_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=400)
    data = json.loads(request.body)
    post = data.get("post", "")
    post = Post.objects.create(
        author=request.user, content=post)
    post.save()
    return JsonResponse({"message": "success"})


def index(request):
    # if the user is not logged in redirect them to the login page
    return render(request, "network/index.html") if request.user.is_authenticated else HttpResponseRedirect(reverse("login"))


def login_view(request):
    # if the user is logged in automatically redirect them to the index page
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method != "POST":
        return render(request, "network/login.html")
    # Attempt to sign user in
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is None:
        return render(request, "network/login.html", {
            "message": "Invalid username and/or password."
        })
    login(request, user)
    return HttpResponseRedirect(reverse("index"))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method != "POST":
        return render(request, "network/register.html")
    username = request.POST["username"]
    email = request.POST["email"]

    # Ensure password matches confirmation
    password = request.POST["password"]
    confirmation = request.POST["confirmation"]
    if password != confirmation:
        return render(request, "network/register.html", {
            "message": "Passwords must match."
        })

    # Attempt to create new user
    try:
        user = User.objects.create_user(username, email, password)
        user.save()
    except IntegrityError:
        return render(request, "network/register.html", {
            "message": "Username already taken."
        })
    login(request, user)
    return HttpResponseRedirect(reverse("index"))
