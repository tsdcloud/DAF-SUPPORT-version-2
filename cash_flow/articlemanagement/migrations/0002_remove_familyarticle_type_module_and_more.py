# Generated by Django 5.0.1 on 2024-04-01 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articlemanagement', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='familyarticle',
            name='type_module',
        ),
        migrations.RemoveField(
            model_name='historicalfamilyarticle',
            name='type_module',
        ),
        migrations.AddField(
            model_name='familyarticle',
            name='type_Module',
            field=models.CharField(choices=[('DMD', 'DMD'), ('RECETTE', 'RECETTE')], default='DMD', max_length=255),
        ),
        migrations.AddField(
            model_name='historicalfamilyarticle',
            name='type_Module',
            field=models.CharField(choices=[('DMD', 'DMD'), ('RECETTE', 'RECETTE')], default='DMD', max_length=255),
        ),
    ]
