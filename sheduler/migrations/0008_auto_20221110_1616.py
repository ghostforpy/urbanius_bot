# Generated by Django 4.0.6 on 2022-11-10 13:16

from django.db import migrations

def create_profile_approved_message_template(apps, schema_editor):
    MessageTemplates = apps.get_model('sheduler', 'MessageTemplates')
    MessageTemplates.objects.create(
        code="profile_approved_message",
        name="Шаблон сообщения одобрения анкеты пользователя",
        text="Ваша регистрация подтверждена. Наберите /start для обновления меню."
    )

class Migration(migrations.Migration):

    dependencies = [
        ('sheduler', '0007_auto_20221109_0059'),
    ]

    operations = [
        migrations.RunPython(create_profile_approved_message_template),
    ]
