from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    Profile, Skill, Project, Experience, Education,
    Category, Tag, BlogPost, Comment, ContactMessage
)

# Register your models here.

# Configuration personnalisée pour l'admin
admin.site.site_header = "Portfolio Administration"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Tableau de bord"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'phone', 'email']
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('user', 'bio', 'location', 'birth_date', 'avatar', 'cv')
        }),
        ('Contact', {
            'fields': ('phone', 'email')
        }),
        ('Réseaux sociaux', {
            'fields': ('github_url', 'linkedin_url', 'twitter_url', 'instagram_url', 'website_url'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'level', 'colored_level']
    list_filter = ['category']
    list_editable = ['level']
    search_fields = ['name']
    ordering = ['category', 'name']
    
    def colored_level(self, obj):
        if obj.level >= 80:
            color = '#22C55E'  # Vert
        elif obj.level >= 60:
            color = '#F59E0B'  # Orange
        else:
            color = '#EF4444'  # Rouge
        
        return format_html(
            '<div style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; text-align: center; font-weight: bold;">'
            '{}%</div>',
            color, obj.level
        )
    colored_level.short_description = 'Niveau'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'featured', 'created_date', 'tech_count', 'image_preview']
    list_filter = ['featured', 'created_date', 'technologies']
    search_fields = ['title', 'description']
    filter_horizontal = ['technologies']
    date_hierarchy = 'created_date'
    ordering = ['-created_date']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'short_description', 'featured', 'order')
        }),
        ('Médias', {
            'fields': ('image',)
        }),
        ('Liens', {
            'fields': ('github_url', 'live_url')
        }),
        ('Technologies', {
            'fields': ('technologies',)
        }),
    )
    
    def tech_count(self, obj):
        return obj.technologies.count()
    tech_count.short_description = 'Technologies'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 4px;" />',
                obj.image.url
            )
        return "Pas d'image"
    image_preview.short_description = 'Aperçu'

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['position', 'company', 'start_date', 'end_date', 'current', 'location']
    list_filter = ['current', 'start_date']
    search_fields = ['position', 'company', 'description']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'institution', 'field', 'start_date', 'end_date', 'current']
    list_filter = ['current', 'start_date']
    search_fields = ['degree', 'institution', 'field']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'colored_name', 'post_count', 'slug']
    list_editable = ['color']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def colored_name(self, obj):
        return format_html(
            '<div style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; display: inline-block;">{}</div>',
            obj.color, obj.name
        )
    colored_name.short_description = 'Couleur'
    
    def post_count(self, obj):
        return obj.blogpost_set.count()
    post_count.short_description = 'Articles'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def post_count(self, obj):
        return obj.blogpost_set.count()
    post_count.short_description = 'Articles'

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'author', 'category', 'featured', 'published_date', 'views', 'image_preview']
    list_filter = ['status', 'featured', 'category', 'created_date', 'author']
    search_fields = ['title', 'content', 'excerpt']
    filter_horizontal = ['tags']
    date_hierarchy = 'published_date'
    ordering = ['-created_date']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        ('Métadonnées', {
            'fields': ('author', 'category', 'tags', 'status', 'featured')
        }),
        ('Statistiques', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 4px;" />',
                obj.featured_image.url
            )
        return "Pas d'image"
    image_preview.short_description = 'Image'
    
    # Actions personnalisées
    def make_published(self, request, queryset):
        queryset.update(status='published')
    make_published.short_description = "Marquer comme publié"
    
    def make_draft(self, request, queryset):
        queryset.update(status='draft')
    make_draft.short_description = "Marquer comme brouillon"
    
    actions = ['make_published', 'make_draft']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'created_date', 'active', 'is_reply']
    list_filter = ['active', 'created_date', 'post']
    search_fields = ['name', 'email', 'content']
    date_hierarchy = 'created_date'
    ordering = ['-created_date']
    
    fieldsets = (
        ('Commentaire', {
            'fields': ('post', 'name', 'email', 'content', 'parent')
        }),
        ('Modération', {
            'fields': ('active',)
        }),
    )
    
    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Réponse'
    
    # Actions personnalisées
    def make_active(self, request, queryset):
        queryset.update(active=True)
    make_active.short_description = "Activer les commentaires"
    
    def make_inactive(self, request, queryset):
        queryset.update(active=False)
    make_inactive.short_description = "Désactiver les commentaires"
    
    actions = ['make_active', 'make_inactive']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'email', 'created_date', 'read', 'message_preview']
    list_filter = ['read', 'created_date']
    search_fields = ['name', 'email', 'subject', 'message']
    date_hierarchy = 'created_date'
    ordering = ['-created_date']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_date']
    
    fieldsets = (
        ('Expéditeur', {
            'fields': ('name', 'email', 'created_date')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Statut', {
            'fields': ('read',)
        }),
    )
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Aperçu'
    
    def save_model(self, request, obj, form, change):
        if change:  # Si on modifie un message existant
            obj.read = True
        super().save_model(request, obj, form, change)
    
    # Actions personnalisées
    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
    mark_as_read.short_description = "Marquer comme lu"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)
    mark_as_unread.short_description = "Marquer comme non lu"
    
    actions = ['mark_as_read', 'mark_as_unread']

# Configuration du dashboard
class PortfolioAdminSite(admin.AdminSite):
    site_header = "Portfolio Administration"
    site_title = "Portfolio Admin"
    index_title = "Tableau de bord"
    
    def index(self, request, extra_context=None):
        # Statistiques personnalisées
        extra_context = extra_context or {}
        
        from django.db.models import Count, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Stats générales
        extra_context.update({
            'total_projects': Project.objects.count(),
            'total_posts': BlogPost.objects.filter(status='published').count(),
            'total_comments': Comment.objects.filter(active=True).count(),
            'unread_messages': ContactMessage.objects.filter(read=False).count(),
            
            # Stats récentes (30 derniers jours)
            'recent_posts': BlogPost.objects.filter(
                created_date__gte=timezone.now() - timedelta(days=30)
            ).count(),
            'recent_comments': Comment.objects.filter(
                created_date__gte=timezone.now() - timedelta(days=30)
            ).count(),
        })
        
        return super().index(request, extra_context)

# Remplacer le site admin par défaut
# admin.site = PortfolioAdminSite()
