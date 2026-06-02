from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from axes.signals import user_locked_out
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def log_user_creation_or_update(sender, instance, created, **kwargs):
    """Log user creation and updates for audit trail"""
    if created:
        logger.info(f'New user created: {instance.username} (Role: {instance.role})')
    else:
        logger.info(f'User updated: {instance.username}')


@receiver(user_locked_out)
def log_lockout(sender, request, credentials, **kwargs):
    """Log lockout attempts for security monitoring"""
    username = credentials.get('username', 'unknown')
    ip_address = get_client_ip(request) if request else 'unknown'
    logger.warning(f'User lockout attempt for {username} from IP {ip_address}')


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
