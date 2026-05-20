from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Service, Barber, Review, Appointment, AboutCompany, BarberRequirement, GalleryCategory, GalleryPhoto, Category
from .forms import AppointmentForm, ReviewForm

# --- 1. ГОЛОВНА СТОРІНКА ---
def home(request):
    services = Service.objects.all()
    categories = Category.objects.all() # ДОДАНО: беремо всі категорії для фільтра
    
    context = {
        'services': services,
        'categories': categories, # Передаємо категорії в шаблон
    }
    return render(request, 'services/index.html', context)

# --- 2. СТОРІНКА "ПРО НАС" ---
def about(request):
    about_info = AboutCompany.objects.first()
    requirements = BarberRequirement.objects.all()
    barbers = Barber.objects.all()
    return render(request, 'services/about.html', {
        'about_info': about_info, 
        'requirements': requirements,
        'barbers': barbers
    })

# --- 3. СТОРІНКА "СПЕЦІАЛЬНІ ПРОПОЗИЦІЇ" (АКЦІЇ) ---
def promo(request):
    services = Service.objects.filter(is_promo=True)
    return render(request, 'services/promo.html', {'services': services})

# --- 4. СТОРІНКА "ВІДГУКИ" ---
def reviews(request):
    # Показуємо тільки ті відгуки, які схвалив адмін
    approved_reviews = Review.objects.filter(is_approved=True).order_by('-created_at')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш відгук успішно надіслано на модерацію! Дякуємо!")
            return redirect('reviews')
    else:
        form = ReviewForm()
        
    return render(request, 'services/reviews.html', {'reviews': approved_reviews, 'form': form})

# --- 5. СТОРІНКА "ОНЛАЙН ЗАПИС" ---
def book(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Вашу заявку успішно відправлено! Ми зв'яжемося з вами найближчим часом.")
            return redirect('book')
    else:
        form = AppointmentForm()
    
    # Передаємо всіх майстрів у шаблон, щоб можна було вивести їхні картки
    barbers = Barber.objects.all()
    return render(request, 'services/booking.html', {'form': form, 'barbers': barbers})

# --- 6. API ДЛЯ КАРТКИ МАЙСТРА  ---
# Ця функція віддає дані про майстра (рейтинг, відгуки), коли клієнт обирає його у списку при бронюванні
def get_barber_info(request, barber_id):
    barber = get_object_or_404(Barber, id=barber_id)
    return JsonResponse({
        'name': barber.name,
        'description': barber.description,
        'photo_url': barber.photo.url if barber.photo else '',
        'average_rating': barber.average_rating,
        'reviews_text': barber.reviews_text 
    })


# ФУНКЦІЇ ДЛЯ ГАЛЕРЕЇ

# --- 7. ГОЛОВНА СТОРІНКА ГАЛЕРЕЇ (СПИСОК АЛЬБОМІВ) ---
def gallery(request):
    # Беремо всі категорії (альбоми) і сортуємо від найновіших
    categories = GalleryCategory.objects.all().order_by('-created_at')
    return render(request, 'services/gallery.html', {'categories': categories})

# --- 8. СТОРІНКА КОНКРЕТНОГО АЛЬБОМУ (ФОТОГРАФІЇ) ---
def gallery_detail(request, category_id):
    # Знаходимо потрібний альбом або видаємо 404 помилку
    category = get_object_or_404(GalleryCategory, id=category_id)
    # Беремо всі фото, прив'язані до цього альбому
    photos = category.photos.all().order_by('-uploaded_at')
    
    return render(request, 'services/gallery_detail.html', {'category': category, 'photos': photos})