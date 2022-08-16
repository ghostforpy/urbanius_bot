# Generated by Django 4.0.6 on 2022-08-16 05:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0020_remove_status_stat_id_status_code_and_more'),
        ('events', '0005_alter_events_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventPrices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Стоимость мероприятия')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='events.events', verbose_name='Мероприятие')),
                ('for_status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tgbot.status', verbose_name='Для статуса')),
            ],
            options={
                'verbose_name': 'Стоимость мероприятия',
                'verbose_name_plural': 'Стоимость мероприятий',
                'ordering': ['event'],
            },
        ),
    ]
