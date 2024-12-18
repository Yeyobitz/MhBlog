from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('normal', 'Usuario Normal'),
        ('moderador', 'Moderador'),
        ('admin', 'Administrador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='normal')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class UserRestriction(models.Model):
    RESTRICTION_TYPES = [
        ('posts', 'Restricción de Posts'),
        ('comments', 'Restricción de Comentarios'),
    ]
    
    DURATION_CHOICES = [
        (1, '1 día'),
        (7, '7 días'),
        (30, '30 días'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restrictions')
    restricted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='restrictions_given')
    restriction_type = models.CharField(max_length=20, choices=RESTRICTION_TYPES)
    duration_days = models.IntegerField(choices=DURATION_CHOICES)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    reason = models.TextField()
    
    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = timezone.now() + timezone.timedelta(days=self.duration_days)
        super().save(*args, **kwargs)
    
    def is_active(self):
        return timezone.now() <= self.end_date
    
    def __str__(self):
        return f"{self.user.username} - {self.get_restriction_type_display()} ({self.duration_days} días)"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()
