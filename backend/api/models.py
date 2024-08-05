from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class ColorblindImage(models.Model):
    TYPE_CHOICES = [
        ('anomalous_trichromatic', 'Tricromático Anómalo'),
        ('dichromatic', 'Dicromático'),
        ('achromatic', 'Acromático'),
    ]

    SUBTYPE_CHOICES = [
        ('protanomalous', 'Protanomalous'),
        ('deuteranomalous', 'Deuteranomalous'),
        ('tritanomalous', 'Tritanomalous'),
        ('protanopia', 'Protanopia'),
        ('deuteranopia', 'Deuteranopia'),
        ('tritanopia', 'Tritanopia'),
        # Puedes agregar más subtipos si es necesario
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='colorblind_images/')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    subtype = models.CharField(max_length=50, choices=SUBTYPE_CHOICES, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.uploaded_at}"


