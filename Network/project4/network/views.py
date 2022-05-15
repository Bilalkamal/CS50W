import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms

from .models import User, Post, Like, Follow


def index(request):
    return render(request, "network/index.html")


def follows(request, user_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET requests only"}, status=405)
    try:
        follows = Follow.objects.filter(follower_id=user_id)
        return JsonResponse(follows, safe=False, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)


def followers(request, user_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET requests only"}, status=405)
    try:
        followers = Follow.objects.filter(followed_id=user_id)
        return JsonResponse(followers, safe=False, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)


@login_required
def follow_user(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST requests only"}, status=405)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    if Follow.objects.filter(follower_id=request.user.id, followed_id=user_id).exists():
        Follow.objects.filter(follower_id=request.user.id,
                              followed_id=user_id).delete()
        return JsonResponse({"message": "Unfollowed."}, status=200)
    Follow.objects.create(follower_id=request.user.id, followed_id=user_id)
    return JsonResponse({"message": "Followed."}, status=200)


@login_required
def like_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST requests only"}, status=405)
    try:
        Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    # if the user has already liked the post, unlike it
    if Like.objects.filter(post_id=post_id, user_id=request.user.id).exists():
        Like.objects.filter(post_id=post_id, user_id=request.user.id).delete()
        return JsonResponse({"message": "unliked"}, status=200)
    # otherwise, like the post
    Like.objects.create(post_id=post_id, user_id=request.user.id)
    return JsonResponse({"message": "liked"}, status=200)


@login_required
def modify_post(request, post_id):
    # check if the post is in the database
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    # check if the user is the owner of this post
    if post.author_id != request.user.id:
        return JsonResponse({"error": "You are not the owner of this post."}, status=403)
    # if this is put request, update the post
    if request.method == "PUT":
        post.content = request.POST["content"]
        post.save()
        return JsonResponse(post, status=200)
    # if this is a delete request, delete the post
    elif request.method == "DELETE":
        post.delete()
        return JsonResponse({"message": "Post deleted."}, status=200)


def post_data(request, post_id):
    if request.method == "GET":
        try:
            post = Post.objects.get(id=post_id)
            return JsonResponse(post.serialize(), status=200)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)
    elif request.method in ["DELETE", "PUT"]:
        modify_post(request, post_id)


@login_required
def post_content(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST requests only"}, status=400)
    content = request.POST["content"]
    author = request.user
    post = Post.objects.create(content=content, author=author)
    return JsonResponse({"id": post.id, "content": post.content, "author": post.author.username, "created_at": post.created_at.strftime("%b %d, %Y, %I:%M %p")}, status=201)


def following_posts(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET requests only"}, status=405)
    # get posts where the user is a follower
    posts = Post.objects.filter(author_id__in=Follow.objects.filter(
        follower=request.user.id).values_list('follower', flat=True))
    # serialize the posts and return them
    posts = [post.serialize() for post in posts]
    for post in posts:
        post["likes"] = Like.objects.filter(post_id=post["id"]).count()
    return JsonResponse(posts, safe=False, status=200)


def user_posts(request, user_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET requests only"}, status=400)
    try:
        posts = Post.objects.filter(author_id=user_id).order_by('-created_at')
        return JsonResponse(posts, safe=False, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)


def all_posts(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET requests only"})
    posts = Post.objects.all().order_by('-created_at')
    posts = [post.serialize() for post in posts]
    for post in posts:
        post["likes"] = Like.objects.filter(post_id=post["id"]).count()
    return JsonResponse(posts, safe=False, status=200)


def login_view(request):
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
    if request.method != "POST":
        return render(request, "network/register.html")
    banned_names = ["admin", "root", "user", "guest", "test", "following"]
    if request.POST["username"] in banned_names:
        return render(request, "network/register.html", {
            "message": "Username is not allowed."
        })
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
