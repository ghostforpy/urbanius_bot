# Generated by Django 4.0.6 on 2022-08-06 01:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0003_alter_user_options_remove_user_club_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialNetSites',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название сайта')),
                ('link', models.URLField(verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'Сайт соц. сети',
                'verbose_name_plural': 'Сайты соц. сетей',
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='socialnets',
            options={'ordering': ['user'], 'verbose_name': 'Страница в соц. сети', 'verbose_name_plural': 'Страницы в соц. сети'},
        ),
        migrations.RemoveField(
            model_name='socialnets',
            name='name',
        ),
        migrations.AddField(
            model_name='jobregions',
            name='code',
            field=models.IntegerField(null=True, verbose_name='Код региона'),
        ),
        migrations.AddField(
            model_name='tggroups',
            name='link',
            field=models.CharField(blank=True, max_length=150, verbose_name='Ссылка на группу'),
        ),
        migrations.AlterField(
            model_name='socialnets',
            name='link',
            field=models.URLField(verbose_name='Страница'),
        ),
        migrations.AddField(
            model_name='socialnets',
            name='soc_net_site',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tgbot.socialnetsites', verbose_name='Сайт соц. сети'),
            preserve_default=False,
        ),
    ]
