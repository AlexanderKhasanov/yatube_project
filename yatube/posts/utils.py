from django.core.paginator import Paginator


def get_page(request, posts, posts_on_page):
    paginator = Paginator(posts, posts_on_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
