# from django.shortcuts import render
# from django.views.generic import TemplateView

# Create your views here.
# def folio(request):
#     return render(request, 'index.html')

# class Home(TemplateView):
#     template_name ='index.html'
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .models import (
    Project, Skill, Experience, Education, Profile,
    BlogPost, Category, Tag, Comment, ContactMessage
)

# Vues Portfolio
def home(request):
    """Page d'accueil avec aperçu du portfolio"""
    profile = Profile.objects.first()
    featured_projects = Project.objects.filter(featured=True)[:3]
    skills = Skill.objects.all().order_by('category', '-level')
    latest_posts = BlogPost.objects.filter(status='published')[:3]
    
    context = {
        'profile': profile,
        'featured_projects': featured_projects,
        'skills': skills,
        'latest_posts': latest_posts,
    }
    return render(request, 'home.html', context)

def about(request):
    """Page à propos"""
    profile = Profile.objects.first()
    experiences = Experience.objects.all()
    education = Education.objects.all()
    skills = Skill.objects.all().order_by('category', '-level')
    
    context = {
        'profile': profile,
        'experiences': experiences,
        'education': education,
        'skills': skills,
    }
    return render(request, 'about.html', context)

def portfolio(request):
    """Page portfolio avec tous les projets"""
    projects = Project.objects.all()
    skills = Skill.objects.all().order_by('name')
    
    # Filtrage par technologie
    tech_filter = request.GET.get('tech')
    if tech_filter:
        projects = projects.filter(technologies__name__icontains=tech_filter)
    
    context = {
        'projects': projects,
        'skills': skills,
        'current_tech': tech_filter,
    }
    return render(request, 'portfolio.html', context)

def project_detail(request, project_id):
    """Détail d'un projet"""
    project = get_object_or_404(Project, id=project_id)
    related_projects = Project.objects.exclude(id=project.id)[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'project_detail.html', context)

# Vues Blog
def blog(request):
    """Liste des articles de blog"""
    posts = BlogPost.objects.filter(status='published')
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    # Filtrage
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    search = request.GET.get('search')
    
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    
    if search:
        posts = posts.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search) |
            Q(excerpt__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Articles populaires et récents
    popular_posts = BlogPost.objects.filter(status='published').order_by('-views')[:5]
    recent_posts = BlogPost.objects.filter(status='published')[:5]
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'popular_posts': popular_posts,
        'recent_posts': recent_posts,
        'current_category': category_slug,
        'current_tag': tag_slug,
        'search_query': search,
    }
    return render(request, 'blog_list.html', context)

def blog_detail(request, slug):
    """Détail d'un article de blog"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Incrémenter les vues
    post.views += 1
    post.save()
    
    # Commentaires
    comments = post.comments.filter(active=True, parent=None)
    
    # Articles similaires
    related_posts = BlogPost.objects.filter(
        status='published',
        category=post.category
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
    }
    return render(request, 'blog/blog_detail.html', context)

def blog_category(request, slug):
    """Articles par catégorie"""
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(status='published', category=category)
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/blog_category.html', context)

def blog_tag(request, slug):
    """Articles par tag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = BlogPost.objects.filter(status='published', tags=tag)
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'page_obj': page_obj,
    }
    return render(request, 'blog/blog_tag.html', context)

# Vue Contact
def contact(request):
    """Page de contact"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Votre message a été envoyé avec succès!')
            return redirect('contact')
        else:
            messages.error(request, 'Veuillez remplir tous les champs.')
    
    return render(request, 'contact.html')

