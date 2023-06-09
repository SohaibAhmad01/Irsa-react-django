# Generated by Django 4.1.3 on 2022-12-28 13:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0002_adminuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtpTemp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('generated_time', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='otpuser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
