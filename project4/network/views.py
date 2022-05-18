from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from .models import User, Post, Like, Follow


@login_required(login_url='login')
@csrf_exempt
def follow_user(request, username):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    user = request.user
    user_to_follow = User.objects.get(username=username)
    print(user_to_follow)
    if user == user_to_follow:
        return JsonResponse({"error": "Cannot follow self."}, status=400)
    followers_count = Follow.objects.filter(
        followed_user=user_to_follow).count()

    followed = Follow.objects.filter(
        follower=user, followed_user=user_to_follow).exists()
    if followed:
        Follow.objects.filter(
            follower=user, followed_user=user_to_follow).delete()
        return JsonResponse({"followed": False, "followers_count": followers_count-1}, status=200)
    # create a new follow
    Follow.objects.create(follower=user, followed_user=user_to_follow)
    return JsonResponse({"followed": True, "followers_count": followers_count+1}, status=200)


@login_required(login_url='login')
@csrf_exempt
def like_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    liked = Like.objects.filter(user=request.user, post=post).exists()
    # get like count of that post
    likes_count = Like.objects.filter(post=post).count()
    if liked:
        Like.objects.filter(user=request.user, post=post).delete()
        return JsonResponse({"liked": False, "likes_count": likes_count-1}, status=200)
    else:
        Like.objects.create(user=request.user, post=post)
        return JsonResponse({"liked": True, "likes_count": likes_count+1}, status=200)


@login_required(login_url='login')
@csrf_exempt
def get_profile(request, username=None):
    if not username:
        username = request.user.username
    try:
        user = User.objects.get(username=username)
    except Exception:
        return HttpResponseRedirect(reverse("index"))
    posts = Post.objects.filter(author=user)
    posts_count = posts.count()
    posts = [post.serialize() for post in posts]
    posts = [{
        **post,
        'likes': len(Like.objects.filter(post=post['id']))
    } for post in posts]
    posts = [{**post, 'liked': Like.objects.filter(
        user=request.user, post=post['id']).exists()} for post in posts]

    followers = Follow.objects.filter(followed_user=user).count()
    following = Follow.objects.filter(follower=user).count()

    # check if the current user is following the user
    followed = Follow.objects.filter(
        follower=request.user, followed_user=user).exists()

    context = {
        "author": user.serialize(),
        "posts": posts,
        "followers": followers,
        "following": following,
        "posts_count": posts_count,
        "owner": request.user.username == username,
        "followed": followed,
    }
    return render(request, "network/profile.html", context)


@login_required
@csrf_exempt
def get_following(request):
    return render(request, "network/following.html")


@login_required
@csrf_exempt
def get_following_posts(request):
    # get posts for the users the current user is following
    username = request.user.username
    user = User.objects.get(username=username)
    # get the list of users the current user is following
    following = [follower.follower.id for follower in Follow.objects.filter(
        followed_user=user)]
    following.append(user.id)
    # find posts for the users the current user is following
    posts = Post.objects.filter(author__in=following)

    posts = [post.serialize() for post in posts]
    # get the count of likes for each post
    posts = [{
        **post,
        'likes': len(Like.objects.filter(post=post['id']))
    } for post in posts]
    # for each post find if the user has liked it
    posts = [{**post, 'liked': Like.objects.filter(
        user=request.user, post=post['id']).exists()} for post in posts]
    print(posts)
    return JsonResponse(posts, safe=False)


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
    posts = [{**post, 'liked': Like.objects.filter(
        user=request.user, post=post['id']).exists()} for post in posts]
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
