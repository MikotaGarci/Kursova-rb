from django.db import models

# ==========================================
# 1. ТАБЛИЦЯ ПОСЛУГ (Стрижки)
# ==========================================
class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва послуги")
    price = models.IntegerField(verbose_name="Ціна (грн)")
    duration_min = models.IntegerField(verbose_name="Тривалість (хв)", default=60)
    photo = models.ImageField(upload_to='services/', blank=True, verbose_name="Фото")

    DIFFICULTY_CHOICES = [
        (1, '⭐ Легко'),
        (2, '⭐⭐ Середньо'),
        (3, '⭐⭐⭐ Важко'),
        (4, '⭐⭐⭐⭐ Експерт'),
    ]
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=2, verbose_name="Складність")
    description = models.TextField(blank=True, verbose_name="Опис")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"

# ==========================================
# 2. ТАБЛИЦЯ МАЙСТРІВ (Барбери)
# ==========================================
class Barber(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ім'я майстра")
    
    # Ті самі нові поля, які нам потрібні:
    description = models.TextField(blank=True, verbose_name="Характеристика / Досвід")
    photo = models.ImageField(upload_to='barbers/', blank=True, null=True, verbose_name="Фото майстра")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Майстер"
        verbose_name_plural = "Майстри"

# ==========================================
# 3. ТАБЛИЦЯ ЗАПИСІВ (Бронювання)
# ==========================================
class Appointment(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Послуга")
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, verbose_name="Майстер", null=True)
    
    client_name = models.CharField(max_length=100, verbose_name="Ім'я клієнта")
    client_phone = models.CharField(max_length=20, verbose_name="Телефон")
    
    date = models.DateField(verbose_name="Дата запису")
    time = models.TimeField(verbose_name="Час запису")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Коли створено заявку")

    def __str__(self):
        return f"{self.client_name} до {self.barber} ({self.date} {self.time})"

    class Meta:
        verbose_name = "Запис"
        verbose_name_plural = "Записи"