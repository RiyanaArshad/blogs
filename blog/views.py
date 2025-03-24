from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count
from .models import Blog, BlogAuthor, Comment, Category
from .forms import UserProfileForm

# Create your views here.

def index(request):
    """View function for home page of site."""
    num_blogs = Blog.objects.count()
    num_authors = BlogAuthor.objects.count()
    num_categories = Category.objects.count()
    
    context = {
        'num_blogs': num_blogs,
        'num_authors': num_authors,
        'num_categories': num_categories,
    }
    
    return render(request, 'blog/index.html', context=context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def search_view(request):
    query = request.GET.get('q')
    if query:
        # First try to find an exact match by title
        exact_match = Blog.objects.filter(title__iexact=query).first()
        if exact_match:
            return redirect('blog-detail', pk=exact_match.pk)
            
        # If no exact match, search for partial matches
        blogs = Blog.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__user__username__icontains=query) |
            Q(categories__name__icontains=query)
        ).distinct()
    else:
        blogs = []
    
    return render(request, 'blog/search_results.html', {
        'query': query,
        'blogs': blogs
    })

class BlogListView(generic.ListView):
    model = Blog
    paginate_by = 3
    template_name = 'blog/blog_list.html'

    def get_queryset(self):
        return Blog.objects.all().order_by('-post_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blogs = context['blog_list']
        for blog in blogs:
            blog.liked_by_user = blog.likes.filter(id=self.request.user.id).exists() if self.request.user.is_authenticated else False
        return context

class BlogDetailView(generic.DetailView):
    model = Blog
    template_name = 'blog/blog_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comment_set.all()
        context['liked_by_user'] = self.object.likes.filter(id=self.request.user.id).exists() if self.request.user.is_authenticated else False
        context['total_likes'] = self.object.total_likes()
        return context

@login_required
def like_blog(request):
    if request.method == 'POST':
        blog_id = request.POST.get('blog_id')
        blog = get_object_or_404(Blog, id=blog_id)
        
        if blog.likes.filter(id=request.user.id).exists():
            # User has already liked this blog, remove like
            blog.likes.remove(request.user)
            liked = False
        else:
            # User hasn't liked this blog yet, add like
            blog.likes.add(request.user)
            liked = True
            
        return JsonResponse({
            'liked': liked,
            'total_likes': blog.total_likes()
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

class BloggerListView(generic.ListView):
    model = BlogAuthor
    paginate_by = 10
    template_name = 'blog/blogger_list.html'
    context_object_name = 'blogauthor_list'  # Changed from 'blogger_list' to match template

    def get_queryset(self):
        return BlogAuthor.objects.annotate(
            total_posts=Count('blog'),
            total_comments=Count('blog__comment')
        ).order_by('-total_posts')

class BloggerDetailView(generic.DetailView):
    model = BlogAuthor
    template_name = 'blog/blogger_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blogs'] = self.object.blog_set.all()
        return context

class CategoryListView(generic.ListView):
    model = Category
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.annotate(blog_count=Count('blog')).order_by('-blog_count')

class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = 'blog/category_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blogs'] = self.object.blog_set.all().order_by('-post_date')
        return context

class BlogCommentCreate(LoginRequiredMixin, generic.CreateView):
    model = Comment
    fields = ['content']
    template_name = 'blog/blog_comment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog'] = Blog.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.blog = Blog.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog-detail', kwargs={'pk': self.kwargs['pk']})

@login_required
def update_profile(request):
    try:
        blog_author = BlogAuthor.objects.get(user=request.user)
    except BlogAuthor.DoesNotExist:
        blog_author = BlogAuthor(user=request.user)
        blog_author.save()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=blog_author)
        if form.is_valid():
            form.save()
            return redirect('blogger-detail', pk=blog_author.pk)
    else:
        form = UserProfileForm(instance=blog_author)
    
    return render(request, 'blog/profile_update.html', {'form': form})
