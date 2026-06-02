from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Santa Fe Admin'),
        ('dispatcher', 'Dispatcher'),
        ('viewer', 'Public Viewer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AccountActivity(models.Model):
    ACTION_LOGIN = 'login'
    ACTION_LOGOUT = 'logout'
    ACTION_CHOICES = (
        (ACTION_LOGIN, 'Login'),
        (ACTION_LOGOUT, 'Logout'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = 'Account Activity'
        verbose_name_plural = 'Account Activities'

    def __str__(self):
        return f'{self.user.username} {self.get_action_display()} at {self.timestamp}'
