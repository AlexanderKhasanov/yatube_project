from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('Главная страница')

def show_groups_list(request):
    return HttpResponse('Список групп')

def group_posts(request, slug):
    return HttpResponse('Посты группы')