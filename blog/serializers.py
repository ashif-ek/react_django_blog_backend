from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source="author.username", read_only=True
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "author",           # PK
            "author_username",  # nice to show in UI
            "created",
            "updated",
        ]
        read_only_fields = ["author", "slug", "created", "updated"]
