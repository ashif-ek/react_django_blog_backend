from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models import Q

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer


@api_view(["POST"])
def register_user(request):
    """
    Creates a new user account.
    """
    data = request.data

    # Check if username is already taken
    if User.objects.filter(username=data.get("username")).exists():
        return Response({"error": "Username taken"}, status=400)

    # Create the user with a hashed password
    User.objects.create(
        username=data.get("username"),
        email=data.get("email"),
        password=make_password(data.get("password")),
    )

    return Response({"message": "User created successfully"}, status=201)


@api_view(["GET", "POST"])
def post_list_create(request):
    """
    GET: Returns a list of blog posts, optionally filtered by a search query.
    POST: Creates a new blog post (requires authentication).
    """
    if request.method == "GET":
        posts = Post.objects.all()

        # Implement search functionality
        search_query = request.GET.get("search", "")
        if search_query:
            # Filter posts where title OR content matches the query
            posts = posts.filter(
                Q(title__icontains=search_query) | Q(content__icontains=search_query)
            )

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    # For POST requests, ensure the user is logged in
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Authentication required to create a post."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        # Automatically set the author to the currently logged-in user
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def post_detail(request, slug):
    """
    Retrieves, updates, or deletes a specific blog post by its slug.
    GET: Returns the post details and increments the view count.
    PUT: Updates the post (author only).
    DELETE: Deletes the post (author only).
    """
    post = get_object_or_404(Post, slug=slug)

    if request.method == "GET":
        # Remarkable Feature: Track views
        # We manually increment the view count each time the detailed post is fetched.
        post.views_count += 1
        post.save(update_fields=["views_count"])

        serializer = PostSerializer(post)
        return Response(serializer.data)

    # For PUT and DELETE, strict authentication is required
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Authentication required to modify this post."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Authorization: Only the original author can edit or delete
    if post.author != request.user:
        return Response({"detail": "You do not have permission to edit this post."}, status=403)

    if request.method == "PUT":
        # partial=True allows sending only the fields that need updating
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == "DELETE":
        post.delete()
        return Response(status=204)


@api_view(["GET", "POST"])
def comment_list_create(request, slug):
    """
    GET: List all comments for a specific post.
    POST: Add a new comment to a post (requires authentication).
    """
    # First, find the post. If not found, it returns a 404 error automatically.
    post = get_object_or_404(Post, slug=slug)

    if request.method == "GET":
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Please log in to comment."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            # Associate the comment with the current user and the specific post
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)
