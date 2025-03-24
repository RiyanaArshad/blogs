from django.contrib import admin
from .models import Blog, BlogAuthor, Comment, Category

# Register your models here.

class CommentInline(admin.TabularInline):
    model = Comment
    max_num = 0
    readonly_fields = ('author', 'content', 'post_date')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_date')
    list_filter = ('post_date', 'author', 'categories')
    filter_horizontal = ('categories',)
    inlines = [CommentInline]

@admin.register(BlogAuthor)
class BlogAuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'author', 'post_date')
    list_filter = ('post_date', 'author')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
