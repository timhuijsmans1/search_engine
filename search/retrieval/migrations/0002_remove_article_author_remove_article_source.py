# Generated by Django 4.0.1 on 2022-01-27 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('retrieval', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='author',
        ),
        migrations.RemoveField(
            model_name='article',
            name='source',
        ),
    ]