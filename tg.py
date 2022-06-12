# All the telegram related functionality is here

from telegram.ext import CommandHandler, CallbackQueryHandler
import logging
import time
from db import add_user, valid, get_expired_list, get_expiration
from payments import get_link, get_status
from global_init import API_TOKEN, TERMINAL, PRICE, GROUP_ID
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from babel.dates import format_datetime
DEBUG = False

updater = Updater(API_TOKEN, use_context=True)


def main_menu(update, context):
    id = update.effective_user.id
    paid = valid(id)
    if paid:
        context.bot.send_message(chat_id=id, text=purchased_message(id),
                                 reply_markup=main_menu_keyboard())
    else:
        context.bot.send_message(chat_id=id, text=not_purchased_message())
        purchase_subscription(update, context)


# def purchase_subscription(update, context) -> None:
#     chat_id = update.effective_user.id
#     title = "Confirm subscription"
#     description = "30 Day Subscription to something?"
#     payload = "Custom-Payload"
#     provider_token = PROVIDER_TOKEN
#     currency = "RUB"
#     price = 100
#     prices = [LabeledPrice("30 Day Subscription", price * 100)]
#     context.bot.send_invoice(
#         chat_id, title, description, payload, provider_token, currency, prices
#     )

# def precheckout_callback(update, context):
#     query = update.pre_checkout_query
#     if query.invoice_payload != 'Custom-Payload':
#         query.answer(ok=False, error_message="Something went wrong...")
#     else:
#         query.answer(ok=True)


# def successful_payment_callback(update, context):
#     id = update.effective_user.id
#     update.message.reply_text("Payment confirmed!")
#     updater.bot.unban_chat_member(chat_id=GROUP_ID,
#                                   user_id=id, only_if_banned=True)

#     add_user(id)
#     update.message.reply_text(purchased_message(id),
#                               reply_markup=main_menu_keyboard())

def purchase_subscription(update, context):
    id = update.effective_user.id
    order = f"{time.time()}/{id}"
    url, pid = get_link(TERMINAL, order, PRICE)
    context.bot.send_message(
        chat_id=id, text=payment_check(), reply_markup=payment_check_btn(url, pid))


def check_payment(update, context):
    id = update.effective_user.id
    args = update.callback_query.data.split()
    pid = args[1]
    status = get_status(TERMINAL, pid)
    message_id = update.callback_query.message.message_id
    chat_id = update.callback_query.message.chat.id
    if status == "CONFIRMED":
        context.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id, text="Оплата прошла успешно!")

        updater.bot.unban_chat_member(chat_id=GROUP_ID,
                                      user_id=id, only_if_banned=True)
        add_user(id)
        context.bot.send_message(chat_id=id, text=purchased_message(id),
                                 reply_markup=main_menu_keyboard())
    elif status == "REJECTED":
        context.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id, text="Оплата была отклонена!")
    else:
        text = "Похоже, Вы еще не оплатили... Перейдите по ссылке, чтобы оплатить!"
        if not update.callback_query.message.text == text:
            context.bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=text,
                reply_markup=update.callback_query.message.reply_markup)


def cancel_payment(update, context):
    message_id = update.callback_query.message.message_id
    chat_id = update.callback_query.message.chat.id
    context.bot.edit_message_text(
        chat_id=chat_id, message_id=message_id, text="Платёж отменен!")


def cancel_subscription_warning(update, context):
    context.bot.send_message(chat_id=update.effective_user.id,
                             text="Вы уверены, что хотите отменить свою подписку?",
                             reply_markup=cancel_menu())


def cancel_subscription(update, context):
    id = update.effective_user.id
    paid = valid(id)
    if paid:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Подписка отменена")
        # ban_user(id)
        admin_members = updater.bot.get_chat_administrators(
            chat_id=GROUP_ID)
        admin_id = {member.user.id for member in admin_members}
        if id not in admin_id:
            updater.bot.ban_chat_member(chat_id=GROUP_ID, user_id=id)
    else:
        context.bot.send_message(chat_id=update.effective_user.id,
                                 text="Похоже, что у Вас еще нет подписки")
    main_menu(update, context)


def error(update, context):
    print(f'Update {update} caused error {context.error}')


def ban():
    try:
        ban_list = get_expired_list()
        admin_members = updater.bot.get_chat_administrators(
            chat_id=GROUP_ID)
        admin_id = {str(member.user.id) for member in admin_members}
        for user_id in ban_list:
            if user_id not in admin_id:
                logging.info(f'Banned {user_id}')
                updater.bot.ban_chat_member(chat_id=GROUP_ID, user_id=user_id)
    except:
        logging.error(f'Ban Error')


############################ Keyboards #########################################

def main_menu_keyboard():
    channel_url = "https://t.me/+_P1FdBCSJhkwMDU0"
    help_url = "https://t.me/fundstratru"
    keyboard = [[InlineKeyboardButton('Присоединиться к каналу', callback_data='last', url=channel_url)],
                [InlineKeyboardButton('Cообщить о проблеме', url=help_url)]]
    # [InlineKeyboardButton('Продлить мою подписку', callback_data='renew')]
    if DEBUG:
        keyboard.append([InlineKeyboardButton('Отменить мою подписку',
                                              callback_data='cancel_warning')])
    return InlineKeyboardMarkup(keyboard)


def payment_check_btn(url, pid):
    keyboard = [[InlineKeyboardButton("Оплатить (CБП)", url=url)],
                [InlineKeyboardButton(
                    "Подтвердить платёж", callback_data=f"check_payment {pid}")],
                [InlineKeyboardButton("Отменить", callback_data="cancel_payment")]]
    return InlineKeyboardMarkup(keyboard)


def cancel_menu():
    keyboard = [[InlineKeyboardButton("Да", callback_data="cancel_subscription")],
                [InlineKeyboardButton("Нет", callback_data="menu")]]
    return InlineKeyboardMarkup(keyboard)


############################# Messages #########################################


def not_purchased_message():
    text = (
        "Похоже, что у Вас еще нет подписки. Оплатите по ссылке, чтобы получить подписку."
    )
    return text


def payment_check():
    text = f"После успешной оплаты, вернитесь сюда и нажмите 'Подтвердить платёж'"

    return text


def purchased_message(id):
    expir_date = get_expiration(id)
    if not expir_date:
        return
    expir_str = format_datetime(expir_date, format="d MMM yyyy", locale='ru')
    text = ("✅ Ваша подписка активна. Следующий платёж:\n"
            f"📅 {expir_str}")
    return text

############################# Handlers #########################################


dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', main_menu))
dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern="menu"))
# dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
# dispatcher.add_handler(MessageHandler(
#     Filters.successful_payment, successful_payment_callback))
dispatcher.add_handler(CallbackQueryHandler(
    check_payment, pattern="check_payment .*"))
dispatcher.add_handler(CallbackQueryHandler(
    cancel_payment, pattern="cancel_payment"))
dispatcher.add_handler(CallbackQueryHandler(
    cancel_subscription_warning, pattern="cancel_warning"))
dispatcher.add_handler(CallbackQueryHandler(
    cancel_subscription, pattern="cancel_subscription"))
dispatcher.add_error_handler(error)
