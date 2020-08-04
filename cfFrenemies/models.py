from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, handle , email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not handle:
            raise ValueError("Users must have a Codeforces handle")

        user = self.model(
            handle = handle,
            email = self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_staffuser(self, handle,email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            handle,
            email,
            password = password,
        )
        user.staff = True
        user.save(using = self._db)
        return user

    def create_superuser(self, handle, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            handle,
            email,
            password = password,
        )
        user.staff = True
        user.admin = True
        user.save(using = self._db)
        return user
    
class User(AbstractBaseUser):
    handle = models.CharField(max_length = 100 , unique = True)
    email = models.EmailField(max_length = 255)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser

    USERNAME_FIELD = 'handle'
    REQUIRED_FIELDS = ['email']
    objects = UserManager()

    def get_full_name(self):
        return self.handle

    def get_short_name(self):
        return self.handle

    def __str__(self):
        return self.handle

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

class User_Friend(models.Model):
    friend_handle = models.CharField(max_length = 100)
    friend_of = models.ForeignKey(User , on_delete=models.CASCADE , default = None)

    def __str__(self):
        return self.friend_handle + ' ' + self.friend_of.handle

class User_Team(models.Model):
    creator_handle = models.CharField(max_length = 100)
    handle1 = models.CharField(max_length = 100)
    handle2 = models.CharField(max_length = 100)
    handle3 = models.CharField(max_length = 100)

    def __str__(self):
        a = [self.handle1, self.handle2, self.handle3]
        a.sort()
        return ''.join(a)
