from rest_framework import serializers

from .models import Comment, Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "instagram_id",
            "caption",
            "media_type",
            "timestamp",
            "created_at",
            "updated_at",
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "instagram_comment_id",
            "text",
            "created_at",
        ]


class CommentCreateInputSerializer(serializers.Serializer):
    text = serializers.CharField()
