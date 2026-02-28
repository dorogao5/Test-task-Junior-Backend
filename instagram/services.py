import logging
from typing import Any

from django.db import transaction
from django.utils.dateparse import parse_datetime

from .client import InstagramAPIError, InstagramClient
from .models import Comment, Post

logger = logging.getLogger(__name__)


def get_client() -> InstagramClient:
    return InstagramClient()


def sync_posts() -> dict[str, int]:
    """Sync Instagram media records into local posts via bulk upsert."""
    with get_client() as client:
        media_items = client.get_all_media()

    posts: list[Post] = []
    for media in media_items:
        instagram_id = str(media.get("id", "")).strip()
        if not instagram_id:
            continue

        timestamp_raw = media.get("timestamp")
        timestamp = parse_datetime(timestamp_raw) if isinstance(timestamp_raw, str) else None
        if timestamp is None:
            continue

        posts.append(
            Post(
                instagram_id=instagram_id,
                caption=str(media.get("caption") or ""),
                media_type=str(media.get("media_type") or ""),
                timestamp=timestamp,
            )
        )

    with transaction.atomic():
        Post.objects.bulk_create(
            posts,
            update_conflicts=True,
            unique_fields=["instagram_id"],
            update_fields=["caption", "media_type", "timestamp"],
        )

    logger.info("Synced %d posts from Instagram", len(posts))
    return {"synced": len(posts)}


def create_comment(post_id: int, text: str) -> Comment:
    """Create an Instagram comment for a post and persist it."""
    post = Post.objects.get(pk=post_id)

    with get_client() as client:
        response: dict[str, Any] = client.post_comment(post.instagram_id, text)

    instagram_comment_id = str(response.get("id", "")).strip()
    if not instagram_comment_id:
        raise InstagramAPIError("Instagram API did not return a comment ID", 502)

    return Comment.objects.create(
        post=post,
        instagram_comment_id=instagram_comment_id,
        text=text,
    )
