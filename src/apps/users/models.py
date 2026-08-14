from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    """Кастомная модель пользователя для проекта Ostbox."""
    
    # phone = models.CharField(max_length=20, blank=True)
    
    pass