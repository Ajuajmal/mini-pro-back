# Generated by Django 3.0.3 on 2020-06-25 19:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferralRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_note', models.TextField(blank=True, default='ND', max_length=500)),
                ('referral_status', models.CharField(choices=[('PD', 'PENDING'), ('SH', 'SHORTLIST'), ('DL', 'DELETE')], default='PD', max_length=8)),
                ('notes_to_requester', models.TextField(blank=True, default='PD', max_length=500)),
                ('request_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referral_request_from', to=settings.AUTH_USER_MODEL)),
                ('request_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='referral_request_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]