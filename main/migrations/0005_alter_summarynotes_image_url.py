# Generated by Django 5.1.7 on 2025-03-30 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_summarynotes_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summarynotes',
            name='image_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
