from django.urls import path

from .views import CommentCreateView, PostListView, SyncView

urlpatterns = [
    path("sync/", SyncView.as_view(), name="sync"),
    path("posts/", PostListView.as_view(), name="post-list"),
    path("posts/<int:pk>/comment/", CommentCreateView.as_view(), name="post-comment"),
]
