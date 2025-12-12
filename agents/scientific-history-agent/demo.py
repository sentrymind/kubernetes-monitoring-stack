#!/usr/bin/env python3
"""
Быстрое демо Scientific History Agent
Запуск: python3 demo.py
"""

import sys
import os

# Проверка зависимостей
try:
    import requests
except ImportError:
    print("⚠️  Установка зависимостей...")
    os.system("pip3 install requests -q")
    import requests

from scientific_history_agent import ScientificHistoryAgent

def print_header(text):
    """Печать заголовка"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_result(i, result):
    """Печать одного результата"""
    print(f"{i}. 📄 {result.title[:70]}...")
    if result.authors:
        authors = ", ".join(result.authors[:2])
        if len(result.authors) > 2:
            authors += f" и др. ({len(result.authors)} авторов)"
        print(f"   👤 Авторы: {authors}")
    if result.year:
        print(f"   📅 Год: {result.year}")
    print(f"   🗄️  База: {result.database}")
    if result.url:
        print(f"   🔗 URL: {result.url[:60]}...")
    print(f"   ⭐ Релевантность: {result.relevance_score:.2f}")
    print()

def demo_search(agent, query, max_display=5):
    """Демонстрация поиска"""
    print(f"🔍 Ищу: '{query}'...")
    print()

    try:
        results = agent.search(query)

        if not results:
            print("❌ Результатов не найдено")
            return False

        print(f"✅ Найдено {len(results)} источников!")
        print()
        print("-" * 70)

        for i, result in enumerate(results[:max_display], 1):
            print_result(i, result)

        if len(results) > max_display:
            print(f"... и ещё {len(results) - max_display} результатов")
            print()

        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Главная функция демо"""
    print_header("🤖 Scientific History Agent - ДЕМО")

    print("Этот агент ищет научные источники по истории XX века (1900-1999)")
    print()

    # Создаем агента
    print("⚙️  Инициализация агента...")
    agent = ScientificHistoryAgent()
    agent.config['max_results'] = 10  # Для демо ограничиваем результаты
    print("✅ Агент готов!")

    # Демо запросы
    demo_queries = [
        "Первая мировая война",
        "Революция 1917 года",
        "Великая депрессия"
    ]

    print()
    print("Доступные демо-запросы:")
    for i, q in enumerate(demo_queries, 1):
        print(f"  {i}. {q}")
    print(f"  {len(demo_queries) + 1}. Свой запрос")
    print(f"  0. Запустить все демо-запросы")
    print()

    try:
        choice = input("Выберите номер (Enter для запуска всех): ").strip()

        if not choice or choice == "0":
            # Запуск всех демо-запросов
            print_header("Запуск всех демо-запросов")
            for query in demo_queries:
                demo_search(agent, query, max_display=3)
                print()
        elif choice.isdigit() and 1 <= int(choice) <= len(demo_queries):
            # Выбранный запрос
            query = demo_queries[int(choice) - 1]
            print_header(f"Поиск: {query}")
            demo_search(agent, query)
        elif choice.isdigit() and int(choice) == len(demo_queries) + 1:
            # Свой запрос
            custom_query = input("\nВведите ваш запрос: ").strip()
            if custom_query:
                print_header(f"Поиск: {custom_query}")
                demo_search(agent, custom_query)
        else:
            print("❌ Неверный выбор")
            return

    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
        return

    # Предложение экспорта
    print()
    print("-" * 70)
    print()

    if agent.results_cache:
        export_choice = input("💾 Сохранить результаты? (y/N): ").strip().lower()
        if export_choice == 'y':
            filename = input("Имя файла (по умолчанию demo_results.md): ").strip()
            if not filename:
                filename = "demo_results.md"

            # Определяем формат по расширению
            if filename.endswith('.json'):
                format_type = 'json'
            elif filename.endswith('.csv'):
                format_type = 'csv'
            else:
                format_type = 'markdown'
                if not filename.endswith('.md'):
                    filename += '.md'

            try:
                agent.export_results(filename, format=format_type)
                print(f"✅ Результаты сохранены в {filename}")
            except Exception as e:
                print(f"❌ Ошибка сохранения: {e}")

    print()
    print_header("Демо завершено!")
    print("Для более детальной работы используйте:")
    print()
    print("  python3 scientific_history_agent.py \"ваш запрос\" --output results.md")
    print("  python3 example_usage.py  # Все примеры")
    print("  python3 test_agent.py     # Запуск тестов")
    print()
    print("Документация: README.md")
    print()

if __name__ == "__main__":
    main()
