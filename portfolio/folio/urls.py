from django.urls import path
from . import views



app_name = 'folio'



urlpatterns = [

    # portfolio path

    # path('',views.folio, name='folio'),
    path('', views.home, name = 'home' ),
    # path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('contact/', views.contact, name='contact'),


        # Blog URLs
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/category/<slug:slug>/', views.blog_category, name='blog_category'),
    path('blog/tag/<slug:slug>/', views.blog_tag, name='blog_tag'),
    


]