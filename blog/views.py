from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .models import Post
from .serializers import PostSerializer


@api_view(["POST"])
def register_user(request):
    data = request.data

    if User.objects.filter(username=data.get("username")).exists():
        return Response({"error": "Username taken"}, status=400)

    User.objects.create(
        username=data.get("username"),
        email=data.get("email"),
        password=make_password(data.get("password")),
    )

    return Response({"message": "User created"}, status=201)


@api_view(["GET", "POST"])
def post_list_create(request):
    if request.method == "GET":
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    # POST – requires login
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Authentication required."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)   # Always attach author
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == "GET":
        serializer = PostSerializer(post)
        return Response(serializer.data)

    # PUT/DELETE – requires login
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Authentication required."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Only author can edit/delete
    if post.author != request.user:
        return Response({"detail": "Not allowed"}, status=403)

    if request.method == "PUT":
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == "DELETE":
        post.delete()
        return Response(status=204)
