# Generated by Django 5.1.2 on 2024-12-18 21:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRestriction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restriction_type', models.CharField(choices=[('posts', 'Restricción de Posts'), ('comments', 'Restricción de Comentarios')], max_length=20)),
                ('duration_days', models.IntegerField(choices=[(1, '1 día'), (7, '7 días'), (30, '30 días')])),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField()),
                ('reason', models.TextField()),
                ('restricted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='restrictions_given', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restrictions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
