# Generated by Django 4.0.6 on 2022-11-10 07:33

from django.db import migrations, models
import tgbot.models.business_benefits
import tgbot.models.business_needs


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0051_alter_businessbranches_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='businessbenefits',
            options={'ordering': ['order_number', 'id'], 'verbose_name': 'Польза бизнеса', 'verbose_name_plural': 'Пользы бизнеса'},
        ),
        migrations.AlterModelOptions(
            name='businessneeds',
            options={'ordering': ['order_number', 'id'], 'verbose_name': 'Потребность бизнеса', 'verbose_name_plural': 'Потребности бизнеса'},
        ),
        migrations.AddField(
            model_name='businessbenefits',
            name='order_number',
            field=models.IntegerField(default=tgbot.models.business_benefits.inc, verbose_name='Порялковый номер в списке'),
        ),
        migrations.AddField(
            model_name='businessneeds',
            name='order_number',
            field=models.IntegerField(default=tgbot.models.business_needs.inc, verbose_name='Порялковый номер в списке'),
        ),
    ]
