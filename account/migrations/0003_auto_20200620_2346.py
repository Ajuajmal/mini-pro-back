# Generated by Django 3.0.3 on 2020-06-20 18:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20200620_2340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumni',
            name='contact',
            field=models.CharField(default='', help_text=' your registerd phone number with university if availabe ,your number help us to auto verify your profile', max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='10 digits only ', regex='^[0-9]{10}$')]),
        ),
    ]
