from django.contrib import admin
from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Service, Barber, Review, Appointment, AboutCompany, BarberRequirement, GalleryCategory, GalleryPhoto, Category

# 1. ВІДЖЕТИ ДЛЯ ДАТИ ТА ЧАСУ АКЦІЇ
class PromoTimeWidget(forms.Select):
    def __init__(self, attrs=None):
        choices = [('', '--- Оберіть час ---')]
        # Генеруємо час від 09:00 до 18:00 з кроком 30 хв
        for h in range(9, 19):
            choices.append((f"{h:02d}:00", f"{h:02d}:00"))
            if h != 18:  # 18:30 не потрібно
                choices.append((f"{h:02d}:30", f"{h:02d}:30"))
        super().__init__(attrs, choices=choices)

# Об'єднуємо Дату і Час
class PromoDateTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.DateInput(attrs={'type': 'date', 'style': 'padding: 6px; border-radius: 4px; border: 1px solid #555; background: #222; color: white; margin-right: 10px; cursor: pointer;'}),
            PromoTimeWidget(attrs={'style': 'padding: 6px; border-radius: 4px; border: 1px solid #555; background: #222; color: white; cursor: pointer;'})
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            value = timezone.localtime(value)
            return [value.date(), value.strftime('%H:%M')]
        return [None, None]

# 2. ФОРМА ДЛЯ ПОСЛУГ В АДМІНЦІ
class ServiceAdminForm(forms.ModelForm):
    promo_end_date = forms.SplitDateTimeField(
        widget=PromoDateTimeWidget(),
        required=False,
        label="Діє до (Дата і час)"
    )

    class Meta:
        model = Service
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ОБМЕЖЕННЯ ДАТИ: Від сьогодні і рівно на 30 днів вперед
        today = timezone.localdate()
        max_date = today + timedelta(days=30)
        
        # Додаємо атрибути min та max до віджета
        date_widget = self.fields['promo_end_date'].widget.widgets[0]
        date_widget.attrs['min'] = today.strftime('%Y-%m-%d')
        date_widget.attrs['max'] = max_date.strftime('%Y-%m-%d')


# ІСНУЮЧІ НАЛАШТУВАННЯ АДМІНКИ

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = ('name', 'category', 'price', 'duration_min', 'is_promo', 'promo_end_date')
    list_filter = ('category', 'is_promo', 'difficulty')
    search_fields = ('name', 'description')

@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'barber', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'barber')
    search_fields = ('name', 'text')
    list_editable = ('is_approved',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'service', 'barber', 'date', 'time', 'status')
    list_filter = ('status', 'date', 'barber')
    search_fields = ('client_name', 'client_phone')
    list_editable = ('status',)

@admin.register(AboutCompany)
class AboutCompanyAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(BarberRequirement)
class BarberRequirementAdmin(admin.ModelAdmin):
    list_display = ('text',)


# НАЛАШТУВАННЯ ДЛЯ ГАЛЕРЕЇ
# Дозволяє додавати фотографії прямо всередині сторінки створення категорії
class GalleryPhotoInline(admin.TabularInline):
    model = GalleryPhoto
    extra = 3
    verbose_name = "Фотографія"
    verbose_name_plural = "Завантажити фотографії в цей альбом"

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    inlines = [GalleryPhotoInline]