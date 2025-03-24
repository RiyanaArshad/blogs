from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('blogs/', views.BlogListView.as_view(), name='blogs'),
    path('blog/<int:pk>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('bloggers/', views.BloggerListView.as_view(), name='bloggers'),
    path('blogger/<int:pk>/', views.BloggerDetailView.as_view(), name='blogger-detail'),
    path('blog/<int:pk>/comment/', views.BlogCommentCreate.as_view(), name='blog-comment'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('category/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('search/', views.search_view, name='search'),
    path('blog/like/', views.like_blog, name='like-blog'),
    path('register/', views.register, name='register'),
    path('profile/update/', views.update_profile, name='update-profile'),
]
