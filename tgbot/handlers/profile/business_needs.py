from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from tgbot.handlers.keyboard import make_keyboard
from tgbot.models import User, BusinessNeeds
from .prepares import (
    prepare_company_business_needs,
    prepare_go_start_conversation,
    prepare_create_business_needs
)


def processing_company_business_needs(update: Update, context: CallbackContext):
    if update.message is not None:
        update.message.reply_text(
            "Используйте предложенные варианты.",
            reply_markup=make_keyboard({},"usual",2)
        )
        user = User.objects.get(user_id = update.message.from_user.id)
        prepare_company_business_needs(update, user)
        return
    user = User.objects.get(user_id = update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "done":
        prepare_go_start_conversation(update, context)
        return "working"
    if variant == "create":
        prepare_create_business_needs(update)
        return "create_business_need"
    need = BusinessNeeds.objects.get(id=variant)
    if need in user.business_needs.all():
        user.business_needs.remove(need)
    else:
        user.business_needs.add(need)
    prepare_company_business_needs(update, user)
    return

def processing_create_business_need_message(update: Update, context: CallbackContext):
    if update.message is not None:
        user = User.objects.get(user_id = update.message.from_user.id)
        new_need = BusinessNeeds.objects.filter(
            title__iexact=update.message.text
        )
        if new_need.exists():
            new_need = BusinessNeeds.objects.filter(
                title__iexact=update.message.text
            ).get()
        else:
            new_need = BusinessNeeds.objects.create(
                title=update.message.text[0].upper() + update.message.text[1:]
            )
        user.business_needs.add(new_need)
        prepare_company_business_needs(update, user)
        return "working_business_needs"

def processing_create_business_need_callback_query(update: Update, context: CallbackContext):
    user = User.objects.get(user_id = update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "cancel":
        prepare_company_business_needs(update, user)
        return "working_business_needs"