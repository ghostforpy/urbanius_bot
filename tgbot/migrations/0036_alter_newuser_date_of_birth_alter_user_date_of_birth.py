# Generated by Django 4.0.6 on 2022-11-08 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0035_newuser_business_club_member_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newuser',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True, verbose_name='Дата рождения'),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True, verbose_name='Дата рождения'),
        ),
    ]
