from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from tgbot.handlers.keyboard import make_keyboard
from tgbot.models import User, BusinessBranches
from tgbot.handlers.utils import send_message #, send_photo, fill_file_id, get_no_foto_id, wrong_file_id
from .messages import MAX_BUSINESS_BRANCHES
from .prepares import prepare_company_business_branches, prepare_go_start_conversation


def processing_company_business_branches(update: Update, context: CallbackContext):
    if update.message is not None:
        update.message.reply_text(
            "Используйте предложенные варианты.",
            reply_markup=make_keyboard({},"usual",2)
        )
        user = User.objects.get(user_id = update.message.from_user.id)
        prepare_company_business_branches(update, user)
        return
    user = User.objects.get(user_id = update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "done":
        prepare_go_start_conversation(update, context)
        return "working"
    branch = BusinessBranches.objects.get(id=variant)
    if branch in user.business_branches.all():
        user.business_branches.remove(branch)
        prepare_company_business_branches(update, user)
        return
    else:
        if user.business_branches.count() < MAX_BUSINESS_BRANCHES:
            user.business_branches.add(branch)
        else:
            send_message(
                user_id=update.callback_query.from_user.id,
                text="Не допускается выбрать более {} вариантов".format(MAX_BUSINESS_BRANCHES),
                reply_markup=make_keyboard({},"inline",1)
            )
        prepare_company_business_branches(update, user)
        return