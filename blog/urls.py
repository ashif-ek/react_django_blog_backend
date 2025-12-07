from django.urls import path
from . import views

urlpatterns = [
    # Post endpoints
    path("posts/", views.post_list_create, name="post_list_create"),
    path("posts/<slug:slug>/", views.post_detail, name="post_detail"),

    # Comment endpoints
    path("posts/<slug:slug>/comments/", views.comment_list_create, name="comment_list_create"),

    # Auth endpoints
    path("register/", views.register_user, name="register"),
]
