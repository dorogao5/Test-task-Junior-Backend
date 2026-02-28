from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from instagram.client import InstagramAPIError
from instagram.models import Comment, Post


class CommentCreateTests(TestCase):
    def setUp(self) -> None:
        self.post = Post.objects.create(
            instagram_id="media_1",
            caption="Caption",
            media_type="IMAGE",
            timestamp=timezone.now(),
        )
        self.url = reverse("post-comment", kwargs={"pk": self.post.pk})

    @patch("instagram.services.get_client")
    def test_create_comment_success(self, mock_get_client: MagicMock) -> None:
        mock_client = mock_get_client.return_value.__enter__.return_value
        mock_client.post_comment.return_value = {"id": "12345"}

        response = self.client.post(
            self.url,
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
        mock_client.post_comment.assert_called_once_with(self.post.instagram_id, "Hello")

    def test_create_comment_post_not_found(self) -> None:
        url = reverse("post-comment", kwargs={"pk": 99999})
        response = self.client.post(
            url,
            data={"text": "Hello"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    @patch("instagram.services.get_client")
    def test_create_comment_instagram_not_found(self, mock_get_client: MagicMock) -> None:
        mock_client = mock_get_client.return_value.__enter__.return_value
        mock_client.post_comment.side_effect = InstagramAPIError("Not Found", 404)

        response = self.client.post(
            self.url,
            data={"text": "Hello"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(Comment.objects.count(), 0)

    def test_create_comment_missing_text(self) -> None:
        response = self.client.post(
            self.url,
            data={},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), 0)

    @patch("instagram.services.get_client")
    def test_create_comment_instagram_returns_no_id(self, mock_get_client: MagicMock) -> None:
        mock_client = mock_get_client.return_value.__enter__.return_value
        mock_client.post_comment.return_value = {}

        response = self.client.post(
            self.url,
            data={"text": "Hello"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(Comment.objects.count(), 0)
