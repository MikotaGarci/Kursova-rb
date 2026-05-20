from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import time, timedelta
from django.db.models import Avg

# ВАЛІДАТОРИ ДЛЯ АКЦІЙ
def validate_future_date(value):
    if value and value < timezone.now():
        raise ValidationError("Дата закінчення акції не може бути в минулому!")

def validate_working_hours(value):
    if value:
        local_dt = timezone.localtime(value) if timezone.is_aware(value) else value
        if not (time(9, 0) <= local_dt.time() <= time(18, 0)):
            raise ValidationError("Час закінчення акції має бути в межах робочого графіка (з 09:00 до 18:00)!")

def validate_max_duration(value):
    if value:
        max_allowed_date = timezone.now() + timedelta(days=30)
        if value > max_allowed_date:
            raise ValidationError("Помилка! Акція не може тривати довше 30 днів (1 місяць).")


# МОДЕЛЬ: КАТЕГОРІЇ ПОСЛУГ
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва категорії")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name


# МОДЕЛЬ ПОСЛУГ
class Service(models.Model):
    DIFFICULTY_CHOICES = [
        (1, '⭐ Легко'),
        (2, '⭐⭐ Середньо'),
        (3, '⭐⭐⭐ Важко'),
        (4, '⭐⭐⭐⭐ Експерт')
    ]

    # Зв'язок з категорією
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категорія")
    
    name = models.CharField(max_length=100, verbose_name="Назва послуги")
    price = models.IntegerField(verbose_name="Ціна (грн)")
    old_price = models.IntegerField(null=True, blank=True, verbose_name="Стара ціна (до акції)")
    duration_min = models.IntegerField(default=60, verbose_name="Тривалість (хв)")
    photo = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name="Фото")
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=2, verbose_name="Складність")
    description = models.TextField(blank=True, verbose_name="Опис")
    
    is_promo = models.BooleanField(default=False, verbose_name="🔥 Акційна пропозиція")
    promo_end_date = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Діє до (Дата і час)",
        validators=[validate_future_date, validate_working_hours, validate_max_duration]
    )

    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"

    def __str__(self):
        if self.is_promo:
            return f"🔥 {self.name} (АКЦІЯ!)"
        return self.name

    # АВТОМАТИЧНЕ ВІДКЛЮЧЕННЯ ПРОСТРОЧЕНИХ АКЦІЙ
    def save(self, *args, **kwargs):
        # Якщо галочка "Акція" стоїть, але час вже вийшов
        if self.is_promo and self.promo_end_date:
            if self.promo_end_date < timezone.now():
                self.is_promo = False          # Знімаємо галочку
                self.promo_end_date = None     # Очищаємо дату
                self.old_price = None          # Очищаємо стару ціну

        super().save(*args, **kwargs)


# МОДЕЛЬ МАЙСТРІВ
class Barber(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ім'я майстра")
    description = models.TextField(blank=True, verbose_name="Характеристика / Досвід")
    photo = models.ImageField(upload_to='barbers/', blank=True, null=True, verbose_name="Фото майстра")
    reviews_text = models.TextField(blank=True, verbose_name="Відгуки клієнтів (цитати)")
    
    @property
    def average_rating(self):
        # Беремо всі відгуки цього майстра, які адмін дозволив
        approved_reviews = self.reviews.filter(is_approved=True)
        if approved_reviews.exists():
            # Рахуємо середнє арифметичне всіх зірок
            avg = approved_reviews.aggregate(Avg('rating'))['rating__avg']
            return round(avg, 1) # Округлюємо до 1 цифри (наприклад, 4.8)
        return 5.0 # Якщо відгуків ще немає, показуємо 5.0

    class Meta:
        verbose_name = "Майстер"
        verbose_name_plural = "Майстри"

    def __str__(self):
        return self.name


# МОДЕЛЬ ВІДГУКІВ
class Review(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True, verbose_name="Кого оцінюєте? (Майстер)")
    name = models.CharField(max_length=100, verbose_name="Ім'я клієнта")
    text = models.TextField(verbose_name="Відгук")
    rating = models.IntegerField(
        default=5, 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оцінка (1-5)"
    )
    is_approved = models.BooleanField(default=False, verbose_name="Опублікувати на сайті")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"

    def __str__(self):
        return f"Відгук від {self.name} ({self.rating} зірок)"


# МОДЕЛЬ ЗАПИСІВ (БРОНЮВАННЯ)
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', '⏳ Очікує підтвердження'),
        ('confirmed', '✅ Підтверджено'),
        ('rejected', '❌ Відхилено'),
    ]

    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Послуга")
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, null=True, verbose_name="Майстер")
    client_name = models.CharField(max_length=100, verbose_name="Ім'я клієнта")
    client_phone = models.CharField(max_length=20, verbose_name="Телефон")
    date = models.DateField(verbose_name="Дата запису")
    time = models.TimeField(verbose_name="Час запису")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Коли створено заявку")

    class Meta:
        verbose_name = "Запис"
        verbose_name_plural = "Записи"

    def __str__(self):
        return f"[{self.get_status_display()}] {self.client_name} - {self.date} {self.time}"


# МОДЕЛЬ ІНФОРМАЦІЇ "ПРО НАС"
class AboutCompany(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Опис компанії")

    class Meta:
        verbose_name = "Про нас (Опис)"
        verbose_name_plural = "Про нас (Опис)"

    def __str__(self):
        return self.title


# МОДЕЛЬ ВИМОГ ДЛЯ ПРАЦЕВЛАШТУВАННЯ
class BarberRequirement(models.Model):
    text = models.CharField(max_length=255, verbose_name="Вимога")

    class Meta:
        verbose_name = "Вимога для барбера"
        verbose_name_plural = "Вимоги для барбера"

    def __str__(self):
        return self.text


# НОВІ МОДЕЛІ ДЛЯ ГАЛЕРЕЇ

# МОДЕЛЬ КАТЕГОРІЙ ГАЛЕРЕЇ (Альбоми)
class GalleryCategory(models.Model):
    title = models.CharField(max_length=100, verbose_name="Назва категорії (Альбому)")
    cover_image = models.ImageField(upload_to='gallery/covers/', verbose_name="Обкладинка альбому")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Категорія галереї"
        verbose_name_plural = "Категорії галереї"

    def __str__(self):
        return self.title

# МОДЕЛЬ ФОТОГРАФІЙ ГАЛЕРЕЇ
class GalleryPhoto(models.Model):
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='photos', verbose_name="Категорія")
    image = models.ImageField(upload_to='gallery/photos/', verbose_name="Фотографія")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата завантаження")

    class Meta:
        verbose_name = "Фотографія галереї"
        verbose_name_plural = "Фотографії галереї"

    def __str__(self):
        return f"Фото з категорії: {self.category.title}"