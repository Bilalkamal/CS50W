
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API endpoints
    path("posts/", views.all_posts, name="all_posts"),
    path("posts/<int:user_id>", views.user_posts, name="user_posts"),
    path("posts/following", views.following_posts, name="following_posts"),
    path("post", views.post_content, name="post_content"),
    path("post/<int:post_id>", views.post_data, name="post_data"),
    path("like/<int:post_id>", views.like_post, name="like_post"),
    path("follow/<int:user_id>", views.follow_user, name="follow_user"),
    path("followers/<int:user_id>", views.followers, name="followers"),
    path("follows/<int:user_id>", views.follows, name="follows")
]
