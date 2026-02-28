from django.db import models


class Post(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "IMAGE"
        VIDEO = "VIDEO"
        CAROUSEL_ALBUM = "CAROUSEL_ALBUM"

    instagram_id = models.CharField(max_length=64, unique=True)
    caption = models.TextField(blank=True)
    media_type = models.CharField(max_length=32, choices=MediaType.choices)
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Post {self.instagram_id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    instagram_comment_id = models.CharField(max_length=64, unique=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Comment {self.instagram_comment_id} on {self.post_id}"
