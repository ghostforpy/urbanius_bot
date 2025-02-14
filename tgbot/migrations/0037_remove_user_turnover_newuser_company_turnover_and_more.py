# Generated by Django 4.0.6 on 2022-11-08 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0036_alter_newuser_date_of_birth_alter_user_date_of_birth'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='turnover',
        ),
        migrations.AddField(
            model_name='newuser',
            name='company_turnover',
            field=models.CharField(choices=[('under 50 millions', 'До 50 млн. руб.'), ('from 50 to 350 millions', 'От 50 до 350 млн. руб.'), ('from 350 millions to 1 billion', 'От 350 млн. до 1 млрд. руб.'), ('from 1 to 5 billions', 'От 1 до 5 млрд. руб.'), ('more then 5 billions', 'Свыше 5 млрд. руб.')], default='I−', max_length=50, verbose_name='under 50 millions'),
        ),
        migrations.AddField(
            model_name='user',
            name='company_turnover',
            field=models.CharField(choices=[('under 50 millions', 'До 50 млн. руб.'), ('from 50 to 350 millions', 'От 50 до 350 млн. руб.'), ('from 350 millions to 1 billion', 'От 350 млн. до 1 млрд. руб.'), ('from 1 to 5 billions', 'От 1 до 5 млрд. руб.'), ('more then 5 billions', 'Свыше 5 млрд. руб.')], default='I−', max_length=50, verbose_name='under 50 millions'),
        ),
    ]
