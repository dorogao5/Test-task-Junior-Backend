from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone

from instagram.client import InstagramAPIError
from instagram.models import Comment, Post


class CommentCreateTests(TestCase):
    @patch("instagram.services.client.post_comment", return_value={"id": "12345"})
    def test_create_comment_success(self, mocked_post_comment: MagicMock) -> None:
        post = Post.objects.create(
            instagram_id="media_1",
            caption="Caption",
            media_type="IMAGE",
            timestamp=timezone.now(),
        )

        response = self.client.post(
            f"/api/posts/{post.pk}/comment/",
            data={"text": "Hello"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)

        comment = Comment.objects.get()
        self.assertEqual(comment.instagram_comment_id, "12345")
        self.assertEqual(comment.text, "Hello")

        payload = response.json()
        self.assertEqual(payload["instagram_comment_id"], "12345")
        self.assertEqual(payload["text"], "Hello")
        mocked_post_comment.assert_called_once_with(post.instagram_id, "Hello")

    def test_create_comment_post_not_found(self) -> None:
        response = self.client.post(
            "/api/posts/999/comment/",
            data={"text": "Hello"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    @patch("instagram.services.client.post_comment")
    def test_create_comment_instagram_not_found(self, mocked_post_comment: MagicMock) -> None:
        post = Post.objects.create(
            instagram_id="media_2",
            caption="Caption",
            media_type="IMAGE",
            timestamp=timezone.now(),
        )
        mocked_post_comment.side_effect = InstagramAPIError("Not Found", 404)

        response = self.client.post(
            f"/api/posts/{post.pk}/comment/",
            data={"text": "Hello"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(Comment.objects.count(), 0)
