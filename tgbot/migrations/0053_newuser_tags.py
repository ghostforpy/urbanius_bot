# Generated by Django 4.0.6 on 2022-11-10 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0052_alter_businessbenefits_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='newuser',
            name='tags',
            field=models.TextField(blank=True, null=True, verbose_name='Тэги'),
        ),
    ]
