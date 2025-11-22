from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.post_list_create, name="post_list_create"),
    path("posts/<slug:slug>/", views.post_detail, name="post_detail"),
    path("register/", views.register_user),

]
