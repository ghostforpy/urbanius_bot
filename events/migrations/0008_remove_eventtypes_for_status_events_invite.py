# Generated by Django 4.0.6 on 2022-08-16 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_alter_eventprices_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventtypes',
            name='for_status',
        ),
        migrations.AddField(
            model_name='events',
            name='invite',
            field=models.FileField(blank=True, null=True, upload_to='events', verbose_name='Файл с приглашением'),
        ),
    ]
