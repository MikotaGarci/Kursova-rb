from django.urls import path
from . import views

urlpatterns = [
    # Основні сторінки сайту
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('promo/', views.promo, name='promo'),
    path('reviews/', views.reviews, name='reviews'),
    path('book/', views.book, name='book'),
    
    # API для миттєвого оновлення рейтингу майстра на сторінці запису
    path('api/barber/<int:barber_id>/', views.get_barber_info, name='get_barber_info'),

    # Сторінки галереї
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/<int:category_id>/', views.gallery_detail, name='gallery_detail'),
]