from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    #path('groups/', views.show_groups_list),
    #path('groups/<slug:slug>/', views.group_posts),
]