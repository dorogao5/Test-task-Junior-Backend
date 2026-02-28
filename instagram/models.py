from django.db import models


class Post(models.Model):
    instagram_id = models.CharField(max_length=64, unique=True)
    caption = models.TextField(blank=True)
    media_type = models.CharField(max_length=32)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    instagram_comment_id = models.CharField(max_length=64)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
