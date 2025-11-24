#!/bin/bash
# Скрипт для быстрого запуска бота

echo "☕ Coffee Shop Telegram Bot - Запуск"
echo "=================================="
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден!"
    echo "Установите Python 3.8 или выше"
    exit 1
fi

echo "✅ Python найден: $(python3 --version)"
echo ""

# Проверка токена
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN не установлен!"
    echo ""
    echo "Как получить токен:"
    echo "1. Откройте @BotFather в Telegram"
    echo "2. Отправьте /newbot"
    echo "3. Следуйте инструкциям"
    echo "4. Скопируйте токен"
    echo ""
    echo "Как установить токен:"
    echo "  export TELEGRAM_BOT_TOKEN='ваш_токен'"
    echo ""
    echo "Или создайте .env файл:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    exit 1
fi

echo "✅ Токен установлен"
echo ""

# Проверка зависимостей
echo "📦 Проверка зависимостей..."
if ! python3 -c "import telegram" 2>/dev/null; then
    echo "⚠️  python-telegram-bot не установлен"
    echo "Устанавливаю..."
    pip3 install python-telegram-bot -q
    echo "✅ Зависимости установлены"
else
    echo "✅ Зависимости в порядке"
fi

echo ""
echo "🚀 Запуск бота..."
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""
echo "=================================="
echo ""

# Запуск бота
python3 coffee_bot.py
