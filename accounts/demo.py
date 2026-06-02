import logging

from axes.models import AccessAttempt
from django.contrib.auth import get_user_model
from django.db import DatabaseError, ProgrammingError

logger = logging.getLogger(__name__)

DEMO_PASSWORD = 'password123'
DEMO_USERS = [
    {
        'username': 'superadmin',
        'email': 'superadmin@alertgov.local',
        'role': 'admin',
        'first_name': 'Super',
        'last_name': 'Admin',
        'is_superuser': True,
        'is_staff': True,
    },
    {
        'username': 'admin',
        'email': 'admin@alertgov.local',
        'role': 'admin',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_superuser': False,
        'is_staff': True,
    },
    {
        'username': 'dispatcher',
        'email': 'dispatcher@alertgov.local',
        'role': 'dispatcher',
        'first_name': 'Dispatcher',
        'last_name': 'Officer',
        'is_superuser': False,
        'is_staff': False,
    },
    {
        'username': 'viewer',
        'email': 'viewer@alertgov.local',
        'role': 'viewer',
        'first_name': 'Public',
        'last_name': 'Viewer',
        'is_superuser': False,
        'is_staff': False,
    },
]


def ensure_demo_accounts():
    """Create/reset demo accounts used by the public login page."""
    User = get_user_model()

    try:
        AccessAttempt.objects.all().delete()

        for user_data in DEMO_USERS:
            username = user_data['username']
            user = User.objects.filter(username=username).first()
            if user is None:
                user = User(username=username)

            user.email = user_data['email']
            user.role = user_data['role']
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.is_active = True
            user.is_superuser = user_data['is_superuser']
            user.is_staff = user_data['is_staff']
            user.set_password(DEMO_PASSWORD)
            user.save()

        return True
    except (DatabaseError, ProgrammingError) as exc:
        logger.warning('Could not ensure demo accounts: %s', exc)
        return False
