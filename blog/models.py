from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200, help_text="Enter a blog category (e.g. Programming)")
    description = models.TextField(max_length=500, help_text="Enter a description for this category")

    class Meta:
        verbose_name_plural = "Categories"

    def get_absolute_url(self):
        return reverse('category-detail', args=[str(self.id)])

    def __str__(self):
        return self.name

class BlogAuthor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, help_text="Enter your bio details here")

    def get_absolute_url(self):
        return reverse('blogger-detail', args=[str(self.id)])

    def __str__(self):
        return self.user.username

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Write your blog content here")
    author = models.ForeignKey(BlogAuthor, on_delete=models.SET_NULL, null=True)
    post_date = models.DateTimeField(default=datetime.now)
    categories = models.ManyToManyField(Category, help_text="Select categories for this blog")
    likes = models.ManyToManyField(User, related_name='blog_likes', blank=True)

    class Meta:
        ordering = ['-post_date']

    def total_likes(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse('blog-detail', args=[str(self.id)])

    def __str__(self):
        return self.title

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField(max_length=1000, help_text="Enter your comment here")
    post_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['post_date']

    def __str__(self):
        return f'{self.content[:75]}...'
