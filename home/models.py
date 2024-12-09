from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='email address')
    first_name = models.CharField(max_length=30, blank=True, verbose_name='first name')
    last_name = models.CharField(max_length=30, blank=True, verbose_name='last name')
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        verbose_name='phone number'
    )
    date_of_birth = models.DateField(auto_now_add=False, null=True, blank=True)
    pin_code = models.BigIntegerField(default=1)
    village = models.CharField(max_length=20)
    district = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True, verbose_name='address')
    is_active = models.BooleanField(default=True, verbose_name='active')
    is_staff = models.BooleanField(default=False, verbose_name='staff status')
    role = models.CharField(max_length=20, 
                            choices=(
                                ("admin","admin"),
                                ("user","user"),
                                ("semi-admin","semi-admin"),
                            
                            ),
                            default='user'
                            )
    
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='date joined')
   

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name","date_of_birth","district","state", "phone_number"]

   
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

        
    def __str__(self):
        return str(self.first_name + " " + self.last_name)

