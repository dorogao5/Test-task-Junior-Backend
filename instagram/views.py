from typing import Any

from rest_framework import generics, status
from rest_framework.pagination import CursorPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .client import InstagramAPIError
from .models import Post
from .serializers import CommentCreateInputSerializer, CommentSerializer, PostSerializer
from . import services


class PostCursorPagination(CursorPagination):
    page_size = 20
    ordering = "-timestamp"


class SyncView(APIView):
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            result = services.sync_posts()
        except InstagramAPIError as exc:
            return Response({"error": exc.message}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(result, status=status.HTTP_200_OK)


class PostListView(generics.ListAPIView):
    queryset = Post.objects.all().order_by("-timestamp")
    serializer_class = PostSerializer
    pagination_class = PostCursorPagination


class CommentCreateView(APIView):
    def post(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        input_serializer = CommentCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        text: str = input_serializer.validated_data["text"]

        try:
            comment = services.create_comment(post_id=pk, text=text)
        except Post.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        except InstagramAPIError as exc:
            return Response({"error": exc.message}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
