# Generated by Django 4.0.6 on 2022-11-13 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0058_alter_businessbenefits_order_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tggroups',
            name='show_for_users',
            field=models.BooleanField(default=False, verbose_name='Показывать пользователям'),
        ),
    ]
