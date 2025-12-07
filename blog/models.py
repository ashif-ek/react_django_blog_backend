from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import math

# We get the user model this way to ensure compatibility if we ever use a custom user model.
User = get_user_model()


class Post(models.Model):
    """
    Represents a blog post in our application.
    It holds the title, content, author information, and tracks engagement metrics
    like views and estimated reading time.
    """
    title = models.CharField(max_length=200, help_text="The headline of the article")
    # A slug is a URL-friendly version of the title (e.g., "Hello World" -> "hello-world")
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField(help_text="The main body text of the article")

    # Link the post to a User. If the user is deleted, their posts are also deleted (CASCADE).
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    # Automatically set these timestamps when created or updated
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # -- New Remarkable Features --
    # Track how many times this post has been viewed
    views_count = models.PositiveIntegerField(default=0)
    # Estimated time in minutes to read this article
    reading_time = models.PositiveIntegerField(default=0, help_text="Estimated reading time in minutes")

    class Meta:
        # Show the newest posts first
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        """
        Overriding the save method to automatically generate a unique slug
        and calculate the reading time before saving to the database.
        """
        if not self.slug:
            # Generate a basic slug from the title
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            # Ensure uniqueness: if "my-post" exists, try "my-post-1", "my-post-2", etc.
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Calculate reading time: Average reading speed is about 200 words per minute.
        if self.content:
            word_count = len(self.content.split())
            # Ceil ensures we say "1 min" even for short posts, rather than "0 min"
            self.reading_time = max(1, math.ceil(word_count / 200))

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (by {self.author.username})"


class Comment(models.Model):
    """
    Allows users to leave feedback on posts.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]  # Oldest comments first (conversation style)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
