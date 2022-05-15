from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_superuser": self.is_superuser,
            "is_staff": self.is_staff,
            "is_active": self.is_active,
            "date_joined": self.date_joined,
            "last_login": self.last_login,
        }


class Post(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content[:20]

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "author": self.author.username
        }


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='liker')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='liked_post')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} likes {self.post.content[:20]}'

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "post": self.post.serialize(),
            "date": self.date
        }


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE)
    followed_user = models.ForeignKey(
        User, related_name='followed_user', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.follower.username} follows {self.followed_user.username}'

    def serialize(self):
        return {
            "id": self.id,
            "follower": self.follower.username,
            "followed_user": self.followed_user.username,
            "date": self.date
        }
