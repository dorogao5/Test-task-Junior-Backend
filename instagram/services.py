from typing import Any

from django.utils.dateparse import parse_datetime

from .client import InstagramAPIError, InstagramClient
from .models import Comment, Post

client = InstagramClient()


def sync_posts() -> dict[str, int]:
    """Sync Instagram media records into local posts."""
    media_items = client.get_all_media()
    synced = 0

    for media in media_items:
        instagram_id = str(media.get("id", "")).strip()
        if not instagram_id:
            continue

        timestamp_raw = media.get("timestamp")
        timestamp = parse_datetime(timestamp_raw) if isinstance(timestamp_raw, str) else None
        if timestamp is None:
            continue

        Post.objects.update_or_create(
            instagram_id=instagram_id,
            defaults={
                "caption": str(media.get("caption") or ""),
                "media_type": str(media.get("media_type") or ""),
                "timestamp": timestamp,
            },
        )
        synced += 1

    return {"synced": synced}


def create_comment(post_id: int, text: str) -> Comment:
    """Create an Instagram comment for a post and persist it."""
    post = Post.objects.get(pk=post_id)
    response: dict[str, Any] = client.post_comment(post.instagram_id, text)
    instagram_comment_id = str(response.get("id", "")).strip()

    return Comment.objects.create(
        post=post,
        instagram_comment_id=instagram_comment_id,
        text=text,
    )
