from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Шлях до адмін-панелі
    path('admin/', admin.site.urls),
    
    # Перенаправляємо всі інші запити у твій додаток services
    path('', include('services.urls')),
]

# Налаштування, щоб Джанго міг показувати завантажені фотографії (галерею, майстрів)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)