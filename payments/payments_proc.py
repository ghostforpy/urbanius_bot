
from telegram import ParseMode,  Update, LabeledPrice, Bot
from telegram.ext import (
    Dispatcher, CommandHandler,PreCheckoutQueryHandler,
    MessageHandler, CallbackQueryHandler,
    Filters, CallbackContext, ConversationHandler
)
from django.conf import settings
from tgbot.models import User, Status
from payments.models import Payments
 
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.utils import send_message
from tgbot.utils import extract_user_data_from_update


def send_invois_to_tg(user,obj,payment_request):
    """Sends an invoice with shipping-payment."""
    str_request = str(payment_request)
    title = obj.name
    description = str_request
    payload = "URBANIUS_CLUB"
    currency = "RUB"
    price = payment_request.price
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice(str_request, int(price * 100))]
    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    bot = Bot(settings.TELEGRAM_TOKEN)
    bot.send_invoice(
        user.user_id,
        title,
        description,
        payload,
        settings.PAYMENT_PROVIDER_TOKEN,
        currency,
        prices,
        need_name=True,
        need_phone_number=True,
        need_email=True,
    )
    return True

# after (optional) shipping, it's the pre-checkout
def manage_precheckout_callback(update: Update, context: CallbackContext) -> None:
    """Answers the PreQecheckoutQuery"""
    user_id = update.pre_checkout_query.from_user.id
    query = update.pre_checkout_query
    if context.user_data.get("payment_started"):
        # check the payload, is this from your bot?
        if query.invoice_payload != "URBANIUS_CLUB":
            # answer False pre_checkout_query
            query.answer(ok=False, error_message="Что-то пошло не так...")
            context.user_data["payment_started"] = False
            send_message(user_id=user_id, text = "Что-то пошло не так...")
            return False
        else:
            query.answer(ok=True)
            return True
    else:
        query.answer(ok=False, error_message="Срок платежа прошел. Начните новый платеж")
        send_message(user_id=user_id, text = "Срок платежа прошел. Начните новый платеж")
        return False


def finish_payment(query, user, payment_request):
    payment = Payments()
    payment.user = user
    payment.price = payment_request.price
    payment.invoice_payload = query.invoice_payload
    payment.provider_payment_charge_id = query.provider_payment_charge_id
    payment.telegram_payment_charge_id = query.telegram_payment_charge_id
    payment.email = query.order_info.email
    payment.name = query.order_info.name
    payment.phone_number = query.order_info.phone_number
    payment.total_amount = query.total_amount/100
    payment.save()
    
    payment_request.payment = payment
    payment_request.payed = True
    payment_request.save()
    send_message(user_id=user.user_id, text = "Спасибо за Ваш платеж!")
    return True
