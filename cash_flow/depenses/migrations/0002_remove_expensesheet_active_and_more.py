# Generated by Django 5.0.1 on 2024-04-01 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('depenses', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expensesheet',
            name='active',
        ),
        migrations.RemoveField(
            model_name='historicalexpensesheet',
            name='active',
        ),
    ]
