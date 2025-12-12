#!/usr/bin/env python3
"""
Создание PDF документации для Telegram бота кофейни
"""

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak,
        Table, TableStyle, Image
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  reportlab не установлен")
    print("Установите: pip install reportlab")

import os

def create_pdf():
    """Создание PDF документа"""

    if not REPORTLAB_AVAILABLE:
        print("❌ Невозможно создать PDF без reportlab")
        print("Запустите: pip install reportlab")
        return False

    # Создаем PDF
    pdf_file = "Coffee_Shop_Bot_Documentation.pdf"
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Стили
    styles = getSampleStyleSheet()

    # Заголовок
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#3498DB'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=9,
        leftIndent=20,
        fontName='Courier',
        textColor=colors.HexColor('#E74C3C'),
        backColor=colors.HexColor('#F8F9FA')
    )

    # Контент
    content = []

    # Титульная страница
    content.append(Spacer(1, 3*cm))
    content.append(Paragraph("☕", title_style))
    content.append(Paragraph("Telegram Бот для Кофейни", title_style))
    content.append(Spacer(1, 1*cm))
    content.append(Paragraph("Полная документация", heading_style))
    content.append(Spacer(1, 0.5*cm))
    content.append(Paragraph("Версия 1.0", normal_style))
    content.append(PageBreak())

    # Содержание
    content.append(Paragraph("Содержание", title_style))
    content.append(Spacer(1, 0.5*cm))

    toc_items = [
        "1. Введение",
        "2. Возможности бота",
        "3. Меню кофейни",
        "4. Быстрый старт",
        "5. Установка",
        "6. Запуск бота",
        "7. Использование",
        "8. Код бота",
        "9. Структура меню",
        "10. Настройка"
    ]

    for item in toc_items:
        content.append(Paragraph(item, normal_style))
        content.append(Spacer(1, 0.3*cm))

    content.append(PageBreak())

    # 1. Введение
    content.append(Paragraph("1. Введение", heading_style))
    content.append(Paragraph(
        "Telegram бот для приёма заказов напитков в кофейне. "
        "Бот имеет красивый интерфейс с inline-кнопками, "
        "корзину покупок и автоматический расчёт стоимости заказа.",
        normal_style
    ))
    content.append(Spacer(1, 0.5*cm))

    # 2. Возможности
    content.append(Paragraph("2. Возможности бота", heading_style))
    features = [
        "☕ Меню с 4 категориями (28+ напитков)",
        "🛒 Корзина покупок с расчётом стоимости",
        "📏 Выбор объёма для каждого напитка",
        "➕ Добавление дополнений (сиропы, сливки, молоко)",
        "✅ Оформление заказа с красивым чеком",
        "📱 Адаптивный интерфейс",
        "🔄 Удобная навигация"
    ]

    for feature in features:
        content.append(Paragraph(f"• {feature}", normal_style))

    content.append(Spacer(1, 0.5*cm))

    # 3. Меню
    content.append(PageBreak())
    content.append(Paragraph("3. Меню кофейни", heading_style))

    menu_data = [
        ['Категория', 'Напитки', 'Цены'],
        ['☕ Классический кофе', 'Эспрессо, Американо,\nКапучино, Латте,\nФлэт уайт, Раф,\nМоккачино', '199-349₽'],
        ['🔥 Горячие напитки', 'Глинтвейн,\nПунши (4 вида)', '219-249₽'],
        ['⭐ Авторский кофе', 'Рафы (4 вида),\nЛатте (3 вида),\nГорячий бамбл', '249-349₽'],
        ['🍵 Не кофе', 'Чай, Матча латте,\nКакао, Бэйбичино,\nГорячий шоколад', '99-299₽'],
        ['➕ Добавки', 'Молоко Alt, Сиропы,\nСливки, Орехи,\nШот эспрессо', '50-100₽'],
    ]

    menu_table = Table(menu_data, colWidths=[4*cm, 7*cm, 3*cm])
    menu_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    content.append(menu_table)
    content.append(Spacer(1, 0.5*cm))

    # 4. Быстрый старт
    content.append(PageBreak())
    content.append(Paragraph("4. Быстрый старт (3 шага)", heading_style))

    content.append(Paragraph("<b>ШАГ 1: Создайте бота</b>", normal_style))
    content.append(Spacer(1, 0.3*cm))
    content.append(Paragraph("1. Откройте @BotFather в Telegram", normal_style))
    content.append(Paragraph("2. Отправьте: /newbot", normal_style))
    content.append(Paragraph("3. Придумайте имя и username", normal_style))
    content.append(Paragraph("4. Скопируйте токен", normal_style))
    content.append(Spacer(1, 0.5*cm))

    content.append(Paragraph("<b>ШАГ 2: Установите зависимости</b>", normal_style))
    content.append(Spacer(1, 0.3*cm))
    content.append(Paragraph("<font name='Courier'>pip install python-telegram-bot</font>", code_style))
    content.append(Spacer(1, 0.5*cm))

    content.append(Paragraph("<b>ШАГ 3: Запустите бота</b>", normal_style))
    content.append(Spacer(1, 0.3*cm))
    content.append(Paragraph("<font name='Courier'>export TELEGRAM_BOT_TOKEN='ваш_токен'</font>", code_style))
    content.append(Paragraph("<font name='Courier'>python coffee_bot.py</font>", code_style))
    content.append(Spacer(1, 0.5*cm))

    # 5. Установка
    content.append(PageBreak())
    content.append(Paragraph("5. Установка на Android (Termux)", heading_style))

    termux_steps = [
        "1. Установите Termux из F-Droid",
        "2. pkg update && pkg upgrade",
        "3. pkg install python git",
        "4. git clone https://github.com/sentrymind/kubernetes-monitoring-stack.git",
        "5. cd kubernetes-monitoring-stack/agents/coffee-shop-bot",
        "6. pip install python-telegram-bot",
        "7. export TELEGRAM_BOT_TOKEN='токен'",
        "8. python coffee_bot.py"
    ]

    for step in termux_steps:
        content.append(Paragraph(step, normal_style))

    content.append(Spacer(1, 0.5*cm))

    # 6. Использование
    content.append(PageBreak())
    content.append(Paragraph("6. Как использовать бота", heading_style))

    usage_flow = [
        "1. Клиент отправляет /start",
        "2. Выбирает категорию напитков",
        "3. Выбирает конкретный напиток",
        "4. Выбирает объём",
        "5. Добавляет дополнения (опционально)",
        "6. Переходит в корзину",
        "7. Оформляет заказ",
        "8. Получает чек с деталями заказа"
    ]

    for step in usage_flow:
        content.append(Paragraph(step, normal_style))

    content.append(Spacer(1, 0.5*cm))

    # 7. Пример заказа
    content.append(Paragraph("<b>Пример заказа:</b>", normal_style))
    content.append(Spacer(1, 0.3*cm))

    example_order = """
🛒 Ваш заказ:

1. Капучино 350мл
   + Сироп
   💰 300₽

2. Американо 450мл
   💰 299₽

━━━━━━━━━━━━━━━
📊 Итого: 599₽
    """

    for line in example_order.strip().split('\n'):
        content.append(Paragraph(line, normal_style))

    content.append(Spacer(1, 0.5*cm))

    # Финальная страница
    content.append(PageBreak())
    content.append(Paragraph("Дополнительная информация", heading_style))
    content.append(Spacer(1, 0.5*cm))

    content.append(Paragraph("<b>Файлы проекта:</b>", normal_style))
    files = [
        "• coffee_bot.py - основной код (444 строки)",
        "• menu_data.py - данные меню",
        "• README.md - полная документация",
        "• QUICKSTART.md - быстрый старт",
        "• INTERFACE.md - описание интерфейса",
        "• requirements.txt - зависимости"
    ]

    for f in files:
        content.append(Paragraph(f, normal_style))

    content.append(Spacer(1, 0.5*cm))
    content.append(Paragraph("<b>GitHub:</b>", normal_style))
    content.append(Paragraph(
        "github.com/sentrymind/kubernetes-monitoring-stack/tree/claude/scientific-sources-agent-011CUd7vAk9s6juvMG5bBi3H/agents/coffee-shop-bot",
        code_style
    ))

    content.append(Spacer(1, 1*cm))
    content.append(Paragraph("Приятного использования! ☕", title_style))

    # Генерация PDF
    doc.build(content)

    print(f"✅ PDF создан: {pdf_file}")
    return True


if __name__ == "__main__":
    print("📄 Создание PDF документации...")

    if create_pdf():
        print("🎉 Готово!")
        print("\nТеперь вы можете:")
        print("1. Открыть Coffee_Shop_Bot_Documentation.pdf")
        print("2. Отправить в Telegram себе или клиентам")
        print("3. Просмотреть на Android смартфоне")
    else:
        print("\n⚠️  Установите reportlab:")
        print("pip install reportlab")
