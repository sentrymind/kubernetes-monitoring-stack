#!/bin/bash
# Quick Start скрипт для Scientific History Agent

set -e

echo "=========================================="
echo "Scientific History Agent - Quick Start"
echo "=========================================="
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Пожалуйста, установите Python 3.8 или выше."
    exit 1
fi

echo "✅ Python 3 найден: $(python3 --version)"
echo ""

# Проверка pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден. Пожалуйста, установите pip3."
    exit 1
fi

echo "✅ pip3 найден: $(pip3 --version)"
echo ""

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt -q

echo "✅ Зависимости установлены"
echo ""

# Проверка конфигурации
if [ ! -f "config.json" ]; then
    echo "❌ Файл config.json не найден!"
    exit 1
fi

echo "✅ Конфигурация найдена"
echo ""

# Демонстрационный поиск
echo "🔍 Выполняю демонстрационный поиск..."
echo ""

python3 scientific_history_agent.py "Первая мировая война" \
    --output demo_results.md \
    --format markdown \
    --max-results 10

echo ""
echo "=========================================="
echo "✅ Quick Start завершён!"
echo "=========================================="
echo ""
echo "Результаты сохранены в demo_results.md"
echo ""
echo "Попробуйте другие примеры:"
echo ""
echo "  python3 scientific_history_agent.py \"Революция 1917\" --output results.json"
echo "  python3 scientific_history_agent.py \"Холодная война\" --max-results 50"
echo "  python3 example_usage.py  # Запуск всех примеров"
echo ""
echo "Документация: README.md"
echo ""
