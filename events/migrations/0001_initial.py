# Generated by Django 3.0.3 on 2020-06-25 17:49

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
            name='EventsByMentor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posted_on', models.DateField(auto_now_add=True)),
                ('event_date', models.DateField()),
                ('event_name', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, default='ND', max_length=500)),
                ('event_status', models.CharField(choices=[('PB', 'PUBLIC EVENT')], default='PB', max_length=8)),
                ('location', models.CharField(blank=True, max_length=500, null=True)),
                ('special_req', models.CharField(blank=True, max_length=1000, null=True)),
                ('conducted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_author', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EventRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_attendee', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_registration', to='events.EventsByMentor')),
            ],
        ),
    ]
