# Generated by Django 4.0.6 on 2022-11-08 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0045_auto_20221108_1707'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessBranches',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Наименование отрасли')),
            ],
            options={
                'verbose_name': 'Отрасль бизнеса',
                'verbose_name_plural': 'Отрасли бизнеса',
                'ordering': ['id'],
            },
        ),
    ]
