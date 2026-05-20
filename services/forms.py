from django import forms
from django.core.exceptions import ValidationError
import re
from datetime import date, timedelta, time, datetime

try:
    from .models import Appointment, Review
except ImportError:
    from services.models import Appointment, Review

TIME_CHOICES = []
base_datetime = datetime.combine(date.today(), time(9, 0))

for i in range(18):
    current_time = (base_datetime + timedelta(minutes=i*30)).time()
    if current_time <= time(17, 30):
        TIME_CHOICES.append((current_time.strftime('%H:%M:%S'), current_time.strftime('%H:%M')))


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'barber', 'client_name', 'client_phone', 'date', 'time']
        
        widgets = {
            'service': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
            'barber': forms.Select(attrs={'class': 'form-select bg-dark text-light border-secondary'}),
            'client_name': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'placeholder': 'Наприклад: Олександр', 
                'minlength': '2', 
                'id': 'name-input'
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'placeholder': '+380...', 
                'maxlength': '13', 
                'id': 'phone-input'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control bg-dark text-light border-secondary', 
                'id': 'id_date'
            }),
            'time': forms.Select(
                choices=TIME_CHOICES, 
                attrs={'class': 'form-select bg-dark text-light border-secondary', 'id': 'id_time'}
            ),
        }

    # Перевірка імені для бронювання ---
    def clean_client_name(self):
        name = self.cleaned_data.get('client_name', '').strip()
        if len(name) < 2:
            raise ValidationError("Ім'я має містити щонайменше 2 літери!")
        if not name[0].isupper():
            raise ValidationError("Ім'я має обов'язково починатися з великої літери!")
        if not re.match(r"^[a-zA-Zа-яА-ЯіІїЇєЄґҐ\s\'-]+$", name):
            raise ValidationError("Ім'я має містити лише літери!")
        return name

    def clean_client_phone(self):
        phone = self.cleaned_data.get('client_phone')
        phone = re.sub(r'\s+', '', phone)
        if not phone.startswith('+380'):
            raise ValidationError("Номер телефону має обов'язково починатися з +380")
        if len(phone) != 13:
            raise ValidationError("Невірний формат. Номер має містити 13 символів")
        if not phone[1:].isdigit():
            raise ValidationError("Номер телефону має містити лише цифри!")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('date')
        appointment_time = cleaned_data.get('time')

        if appointment_date and appointment_time:
            today = date.today()
            
            if appointment_date < today:
                self.add_error('date', "❌ Не можна записатися на минулу дату.")
            elif appointment_date > today + timedelta(days=60):
                self.add_error('date', "❌ Бронювання доступне максимум на 2 місяці вперед.")

            hour = appointment_time.hour
            minute = appointment_time.minute
            weekday = appointment_date.weekday()

            if 12 <= hour < 13:
                self.add_error('time', "❌ З 12:00 до 13:00 обідня перерва.")
            
            if weekday < 5: 
                if hour < 9 or hour > 17 or (hour == 17 and minute > 30):
                    self.add_error('time', "❌ Будні: 09:00 - 18:00 (останній запис о 17:30).")
            else: 
                if hour < 10 or hour > 16 or (hour == 16 and minute > 30):
                    self.add_error('time', "❌ Вихідні: 10:00 - 17:00 (останній запис о 16:30).")

        return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['barber', 'name', 'text', 'rating']
        widgets = {
            'barber': forms.Select(attrs={
                'class': 'form-select bg-dark text-light border-secondary mb-3',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'placeholder': 'Ваше ім\'я'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'placeholder': 'Поділіться враженнями...', 
                'rows': 4
            }),
            'rating': forms.HiddenInput(attrs={'id': 'rating-value'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise ValidationError("Ім'я має містити щонайменше 2 літери!")
        if not name[0].isupper():
            raise ValidationError("Ім'я має обов'язково починатися з великої літери!")
        if not re.match(r"^[a-zA-Zа-яА-ЯіІїЇєЄґҐ\s\'-]+$", name):
            raise ValidationError("Ім'я має містити лише літери! Ніяких цифр або спецсимволів.")
        return name

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating or int(rating) < 1:
            raise ValidationError("Будь ласка, оберіть хоча б одну зірку!")
        return rating