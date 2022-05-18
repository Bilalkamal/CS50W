
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-post", views.create_post, name="create-post"),
    path("all-posts", views.get_all_posts, name="all-posts"),
    path("following", views.get_following, name="following"),
    path("following-posts", views.get_following_posts, name="following-posts"),
    path("profile/", views.get_profile, name="profile"),
    path("profile/<str:username>", views.get_profile, name="profile"),
]
