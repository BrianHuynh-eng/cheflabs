from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from .models import Employees


@receiver(post_save, sender=Employees)
def create_user_for_employee(sender, instance, created, **kwargs):
    CustomUser = get_user_model()

    if hasattr(instance, '_signal_creating_user'):
        return

    if created and not CustomUser.objects.filter(username=instance.account_username).exists():
        user = CustomUser.objects.create_user(
            username=instance.account_username,
            password=instance.account_password,
            phone_number=instance.phone,
        )

        if instance.job_position == 'Owner':
            user.is_staff = False
            user.is_superuser = False

            owner_group, created = Group.objects.get_or_create(name='Owner')
            user.groups.add(owner_group)

        elif instance.job_position == 'Manager':
            user.is_staff = False
            user.is_superuser = False

            management_group, created = Group.objects.get_or_create(name='Management')
            user.groups.add(management_group)

        elif instance.job_position == 'Chef':
            user.is_staff = False
            user.is_superuser = False
            
            chef_group, created = Group.objects.get_or_create(name='Chef')
            user.groups.add(chef_group)

        else:
            user.is_staff = False
            user.is_superuser = False

            employee_group, created = Group.objects.get_or_create(name='Employee')
            user.groups.add(employee_group)

        user.save()

        instance._signal_creating_user = True

        instance.user = user
        instance.save()

        delattr(instance, '_signal_creating_user')

    else:
        print(f"Halt!: A user with username {instance.account_username} already exists.")
