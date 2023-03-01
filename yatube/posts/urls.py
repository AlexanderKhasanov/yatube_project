from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('groups/', views.show_groups_list),
    path('groups/<slug:slug>/', views.group_posts),
]