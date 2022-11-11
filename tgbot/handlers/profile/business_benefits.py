from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from tgbot.handlers.keyboard import make_keyboard
from tgbot.models import User, BusinessBenefits
from .prepares import (
    prepare_go_start_conversation,
    prepare_create_business_benefits,
    prepare_company_business_benefits
)



def processing_create_business_benefit_message(update: Update, context: CallbackContext):
    if update.message is not None:
        new_user = User.objects.get(user_id = update.message.from_user.id)
        new_benefit = BusinessBenefits.objects.filter(
            title__iexact=update.message.text
        )
        if new_benefit.exists():
            new_benefit = BusinessBenefits.objects.filter(
                title__iexact=update.message.text
            ).get()
        else:
            new_benefit = BusinessBenefits.objects.create(
                title=update.message.text[0].upper() + update.message.text[1:]
            )
        new_user.business_benefits.add(new_benefit)
        prepare_company_business_benefits(update, new_user)
        return "working_business_benefits"


def processing_create_business_benefit_callback_query(update: Update, context: CallbackContext):
    new_user = User.objects.get(user_id = update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "cancel":
            prepare_company_business_benefits(update, new_user)
            return "working_business_benefits"


def processing_company_business_benefits(update: Update, context: CallbackContext):
    if update.message is not None:
        update.message.reply_text(
            "Используйте предложенные варианты.",
            reply_markup=make_keyboard({},"usual",2)
        )
        new_user = User.objects.get(user_id = update.message.from_user.id)
        prepare_company_business_benefits(update, new_user)
        return
    new_user = User.objects.get(user_id = update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "create":
        prepare_create_business_benefits(update)
        return "create_business_benefit"
    if variant == "done":
        prepare_go_start_conversation(update, context)
        return "working"
    benefit = BusinessBenefits.objects.get(id=variant)
    if benefit in new_user.business_benefits.all():
        new_user.business_benefits.remove(benefit)
    else:
        new_user.business_benefits.add(benefit)
    prepare_company_business_benefits(update, new_user)
    return