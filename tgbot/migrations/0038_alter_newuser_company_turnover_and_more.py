# Generated by Django 4.0.6 on 2022-11-08 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0037_remove_user_turnover_newuser_company_turnover_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newuser',
            name='company_turnover',
            field=models.CharField(choices=[('under 50 millions', 'До 50 млн. руб.'), ('from 50 to 350 millions', 'От 50 до 350 млн. руб.'), ('from 350 millions to 1 billion', 'От 350 млн. до 1 млрд. руб.'), ('from 1 to 5 billions', 'От 1 до 5 млрд. руб.'), ('more then 5 billions', 'Свыше 5 млрд. руб.')], default='under 50 millions', max_length=50, verbose_name='Оборот компании в год'),
        ),
        migrations.AlterField(
            model_name='user',
            name='company_turnover',
            field=models.CharField(choices=[('under 50 millions', 'До 50 млн. руб.'), ('from 50 to 350 millions', 'От 50 до 350 млн. руб.'), ('from 350 millions to 1 billion', 'От 350 млн. до 1 млрд. руб.'), ('from 1 to 5 billions', 'От 1 до 5 млрд. руб.'), ('more then 5 billions', 'Свыше 5 млрд. руб.')], default='under 50 millions', max_length=50, verbose_name='Оборот компании в год'),
        ),
    ]
