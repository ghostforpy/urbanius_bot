# Generated by Django 4.0.6 on 2022-11-12 13:10

from django.db import migrations

def approve_admin_business_needs(apps, schema_editor):
    BusinessNeeds = apps.get_model('tgbot', 'BusinessNeeds')
    NEEDS = [
        "Взаимодействие с властью",
        "Поиск поставщиков и подрядчиков",
        "Поиск клиентов и заказчиков",
        "Участие в тендерах и электронных торгах",
        "Подбор квалифицированных кадров"
    ]
    BusinessNeeds.objects.filter(title__in=NEEDS).update(admin_aprooved=True)

class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0054_businessneeds_admin_aprooved_and_more'),
    ]

    operations = [
        migrations.RunPython(approve_admin_business_needs),
    ]
