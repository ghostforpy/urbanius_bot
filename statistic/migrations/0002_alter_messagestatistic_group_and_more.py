# Generated by Django 4.0.6 on 2022-08-14 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0018_user_main_photo_id'),
        ('statistic', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagestatistic',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.tggroups', verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='messagestatistic',
            name='messages',
            field=models.IntegerField(default=0, verbose_name='Число сообщений в группе'),
        ),
    ]
