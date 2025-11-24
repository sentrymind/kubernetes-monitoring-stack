#!/usr/bin/env python3
"""
Telegram бот для заказа напитков в кофейне
"""

import logging
import os
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler
)

from menu_data import MENU, EXTRAS

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния разговора
CHOOSING_CATEGORY, CHOOSING_DRINK, CHOOSING_VOLUME, CHOOSING_EXTRAS = range(4)

# Хранилище корзин пользователей (в продакшене использовать БД)
user_carts: Dict[int, List] = {}


def get_cart(user_id: int) -> List:
    """Получить корзину пользователя"""
    if user_id not in user_carts:
        user_carts[user_id] = []
    return user_carts[user_id]


def calculate_cart_total(cart: List) -> int:
    """Рассчитать общую стоимость корзины"""
    return sum(item['price'] for item in cart)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало работы с ботом"""
    user = update.effective_user

    welcome_text = f"""
☕ Добро пожаловать в нашу кофейню, {user.first_name}!

Выберите категорию напитков:
"""

    keyboard = []
    for category in MENU.keys():
        keyboard.append([InlineKeyboardButton(category, callback_data=f"cat_{category}")])

    keyboard.append([InlineKeyboardButton("🛒 Корзина", callback_data="cart")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return CHOOSING_CATEGORY


async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показать напитки в категории"""
    query = update.callback_query
    await query.answer()

    category = query.data.replace("cat_", "")
    context.user_data['current_category'] = category

    keyboard = []
    drinks = MENU[category]

    for drink_name, drink_data in drinks.items():
        # Показываем минимальную цену
        min_price = min(drink_data['volumes'].values())
        keyboard.append([
            InlineKeyboardButton(
                f"{drink_name} - от {min_price}₽",
                callback_data=f"drink_{drink_name}"
            )
        ])

    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_categories")])
    keyboard.append([InlineKeyboardButton("🛒 Корзина", callback_data="cart")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"{category}\n\nВыберите напиток:",
        reply_markup=reply_markup
    )
    return CHOOSING_DRINK


async def show_volumes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показать доступные объёмы"""
    query = update.callback_query
    await query.answer()

    drink_name = query.data.replace("drink_", "")
    context.user_data['current_drink'] = drink_name

    category = context.user_data['current_category']
    volumes = MENU[category][drink_name]['volumes']

    keyboard = []
    for volume, price in volumes.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{volume} - {price}₽",
                callback_data=f"vol_{volume}_{price}"
            )
        ])

    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"cat_{category}")])
    keyboard.append([InlineKeyboardButton("🛒 Корзина", callback_data="cart")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"☕ {drink_name}\n\nВыберите объём:",
        reply_markup=reply_markup
    )
    return CHOOSING_VOLUME


async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Добавить напиток в корзину"""
    query = update.callback_query
    await query.answer("✅ Добавлено в корзину!")

    # Парсим данные
    _, volume, price = query.data.split("_", 2)
    price = int(price)

    drink_name = context.user_data['current_drink']
    category = context.user_data['current_category']
    user_id = update.effective_user.id

    # Добавляем в корзину
    cart = get_cart(user_id)
    cart.append({
        'category': category,
        'drink': drink_name,
        'volume': volume,
        'price': price,
        'extras': []
    })

    # Спрашиваем про добавки
    keyboard = []
    for extra_name, extra_price in EXTRAS["➕ ДОБАВКИ"].items():
        keyboard.append([
            InlineKeyboardButton(
                f"{extra_name} +{extra_price}₽",
                callback_data=f"extra_{extra_name}_{extra_price}"
            )
        ])

    keyboard.append([InlineKeyboardButton("✅ Без добавок", callback_data="no_extras")])
    keyboard.append([InlineKeyboardButton("🛒 К корзине", callback_data="cart")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"✅ {drink_name} {volume} добавлен!\n\nХотите добавить что-нибудь?",
        reply_markup=reply_markup
    )
    return CHOOSING_EXTRAS


async def add_extra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Добавить дополнение к последнему напитку"""
    query = update.callback_query
    await query.answer("✅ Добавка добавлена!")

    user_id = update.effective_user.id
    cart = get_cart(user_id)

    if cart:
        # Парсим данные
        parts = query.data.replace("extra_", "").rsplit("_", 1)
        extra_name = parts[0]
        extra_price = int(parts[1])

        # Добавляем к последнему напитку
        cart[-1]['extras'].append({
            'name': extra_name,
            'price': extra_price
        })
        cart[-1]['price'] += extra_price

    # Показываем меню добавок снова
    keyboard = []
    for extra_name, extra_price in EXTRAS["➕ ДОБАВКИ"].items():
        keyboard.append([
            InlineKeyboardButton(
                f"{extra_name} +{extra_price}₽",
                callback_data=f"extra_{extra_name}_{extra_price}"
            )
        ])

    keyboard.append([InlineKeyboardButton("✅ Готово", callback_data="no_extras")])
    keyboard.append([InlineKeyboardButton("🛒 К корзине", callback_data="cart")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "Ещё добавки?",
        reply_markup=reply_markup
    )
    return CHOOSING_EXTRAS


async def no_extras(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Без добавок - вернуться к меню"""
    query = update.callback_query
    await query.answer()

    keyboard = []
    for category in MENU.keys():
        keyboard.append([InlineKeyboardButton(category, callback_data=f"cat_{category}")])

    keyboard.append([InlineKeyboardButton("🛒 Корзина", callback_data="cart")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "Что-нибудь ещё?\n\nВыберите категорию:",
        reply_markup=reply_markup
    )
    return CHOOSING_CATEGORY


async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показать корзину"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    cart = get_cart(user_id)

    if not cart:
        keyboard = [
            [InlineKeyboardButton("⬅️ К меню", callback_data="back_to_categories")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🛒 Корзина пуста\n\nДобавьте напитки из меню!",
            reply_markup=reply_markup
        )
        return CHOOSING_CATEGORY

    # Формируем текст корзины
    cart_text = "🛒 Ваш заказ:\n\n"

    for i, item in enumerate(cart, 1):
        cart_text += f"{i}. {item['drink']} {item['volume']}\n"

        if item['extras']:
            for extra in item['extras']:
                cart_text += f"   + {extra['name']}\n"

        cart_text += f"   💰 {item['price']}₽\n\n"

    total = calculate_cart_total(cart)
    cart_text += f"━━━━━━━━━━━━━━━\n"
    cart_text += f"📊 Итого: {total}₽"

    keyboard = [
        [InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton("🗑 Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton("⬅️ Продолжить покупки", callback_data="back_to_categories")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(cart_text, reply_markup=reply_markup)
    return CHOOSING_CATEGORY


async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Очистить корзину"""
    query = update.callback_query
    await query.answer("🗑 Корзина очищена")

    user_id = update.effective_user.id
    user_carts[user_id] = []

    keyboard = []
    for category in MENU.keys():
        keyboard.append([InlineKeyboardButton(category, callback_data=f"cat_{category}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "Корзина очищена!\n\nВыберите напитки:",
        reply_markup=reply_markup
    )
    return CHOOSING_CATEGORY


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Оформление заказа"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user = update.effective_user
    cart = get_cart(user_id)

    if not cart:
        await query.edit_message_text("Корзина пуста!")
        return ConversationHandler.END

    # Формируем заказ
    order_text = f"🎉 Заказ оформлен!\n\n"
    order_text += f"👤 Клиент: {user.first_name}\n"
    order_text += f"🆔 ID: {user_id}\n\n"
    order_text += f"📋 Заказ:\n"

    for i, item in enumerate(cart, 1):
        order_text += f"\n{i}. {item['drink']} {item['volume']}"

        if item['extras']:
            order_text += "\n   Добавки:"
            for extra in item['extras']:
                order_text += f"\n   • {extra['name']}"

        order_text += f"\n   💰 {item['price']}₽"

    total = calculate_cart_total(cart)
    order_text += f"\n\n━━━━━━━━━━━━━━━"
    order_text += f"\n📊 ИТОГО: {total}₽"
    order_text += f"\n\n✅ Ваш заказ принят!"
    order_text += f"\n⏰ Ожидайте приготовления"

    # Здесь можно отправить заказ администратору
    # await context.bot.send_message(ADMIN_CHAT_ID, f"Новый заказ:\n{order_text}")

    keyboard = [[InlineKeyboardButton("🏠 Новый заказ", callback_data="new_order")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(order_text, reply_markup=reply_markup)

    # Очищаем корзину
    user_carts[user_id] = []

    return ConversationHandler.END


async def new_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начать новый заказ"""
    query = update.callback_query
    await query.answer()

    keyboard = []
    for category in MENU.keys():
        keyboard.append([InlineKeyboardButton(category, callback_data=f"cat_{category}")])

    keyboard.append([InlineKeyboardButton("🛒 Корзина", callback_data="cart")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "☕ Выберите категорию:",
        reply_markup=reply_markup
    )
    return CHOOSING_CATEGORY


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменить разговор"""
    await update.message.reply_text(
        "Заказ отменен. Используйте /start для нового заказа."
    )
    return ConversationHandler.END


def main():
    """Запуск бота"""
    # Получаем токен из переменной окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        logger.error("Установите токен: export TELEGRAM_BOT_TOKEN='ваш_токен'")
        return

    # Создаём приложение
    application = Application.builder().token(token).build()

    # Создаём обработчик разговора
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_CATEGORY: [
                CallbackQueryHandler(show_category, pattern="^cat_"),
                CallbackQueryHandler(show_cart, pattern="^cart$"),
                CallbackQueryHandler(clear_cart, pattern="^clear_cart$"),
                CallbackQueryHandler(checkout, pattern="^checkout$"),
            ],
            CHOOSING_DRINK: [
                CallbackQueryHandler(show_category, pattern="^cat_"),
                CallbackQueryHandler(show_volumes, pattern="^drink_"),
                CallbackQueryHandler(show_cart, pattern="^cart$"),
                CallbackQueryHandler(start, pattern="^back_to_categories$"),
            ],
            CHOOSING_VOLUME: [
                CallbackQueryHandler(show_category, pattern="^cat_"),
                CallbackQueryHandler(add_to_cart, pattern="^vol_"),
                CallbackQueryHandler(show_cart, pattern="^cart$"),
            ],
            CHOOSING_EXTRAS: [
                CallbackQueryHandler(add_extra, pattern="^extra_"),
                CallbackQueryHandler(no_extras, pattern="^no_extras$"),
                CallbackQueryHandler(show_cart, pattern="^cart$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(start, pattern="^back_to_categories$"),
            CallbackQueryHandler(new_order, pattern="^new_order$"),
        ],
    )

    application.add_handler(conv_handler)

    # Запускаем бота
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
