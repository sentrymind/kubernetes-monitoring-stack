#!/usr/bin/env python3
"""
Примеры использования Scientific History Agent
"""

from scientific_history_agent import ScientificHistoryAgent
import json


def example_basic_search():
    """Базовый пример поиска"""
    print("=" * 80)
    print("Пример 1: Базовый поиск")
    print("=" * 80)

    agent = ScientificHistoryAgent()
    results = agent.search("Вторая мировая война")

    print(f"\nНайдено {len(results)} источников\n")

    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result.title}")
        print(f"   Год: {result.year}")
        print(f"   База данных: {result.database}")
        print()


def example_advanced_search():
    """Расширенный поиск с экспортом результатов"""
    print("=" * 80)
    print("Пример 2: Расширенный поиск с экспортом")
    print("=" * 80)

    # Создание агента с пользовательской конфигурацией
    agent = ScientificHistoryAgent()
    agent.config['max_results'] = 20

    # Поиск
    results = agent.search("Холодная война")

    print(f"\nНайдено {len(results)} источников\n")

    # Экспорт в разные форматы
    agent.export_results("results_cold_war.json", format="json")
    agent.export_results("results_cold_war.md", format="markdown")
    agent.export_results("results_cold_war.csv", format="csv")

    print("Результаты экспортированы в:")
    print("  - results_cold_war.json")
    print("  - results_cold_war.md")
    print("  - results_cold_war.csv")


def example_multiple_queries():
    """Множественные запросы"""
    print("=" * 80)
    print("Пример 3: Множественные запросы")
    print("=" * 80)

    agent = ScientificHistoryAgent()

    queries = [
        "Первая мировая война",
        "Революция 1917 года",
        "Великая депрессия",
        "Космическая гонка"
    ]

    all_results = {}

    for query in queries:
        print(f"\nПоиск: {query}...")
        results = agent.search(query)
        all_results[query] = len(results)
        print(f"  Найдено: {len(results)} источников")

    print("\n" + "=" * 80)
    print("Сводка:")
    print("=" * 80)
    for query, count in all_results.items():
        print(f"{query}: {count} источников")


def example_filter_by_database():
    """Поиск в конкретной базе данных"""
    print("=" * 80)
    print("Пример 4: Поиск в конкретной базе данных")
    print("=" * 80)

    # Поиск только в CrossRef
    agent = ScientificHistoryAgent()
    agent.config['databases'] = ['crossref']

    results = agent.search("История авиации")

    print(f"\nНайдено {len(results)} источников в CrossRef\n")

    for result in results[:3]:
        print(f"- {result.title}")
        print(f"  База данных: {result.database}")
        print()


def example_analysis():
    """Анализ результатов поиска"""
    print("=" * 80)
    print("Пример 5: Анализ результатов")
    print("=" * 80)

    agent = ScientificHistoryAgent()
    results = agent.search("Индустриализация СССР")

    # Статистика по годам
    years = {}
    for result in results:
        if result.year:
            years[result.year] = years.get(result.year, 0) + 1

    print("\nРаспределение публикаций по годам:")
    for year in sorted(years.keys()):
        print(f"  {year}: {'█' * years[year]} ({years[year]})")

    # Статистика по базам данных
    databases = {}
    for result in results:
        databases[result.database] = databases.get(result.database, 0) + 1

    print("\nРаспределение по базам данных:")
    for db, count in databases.items():
        print(f"  {db}: {count} источников")

    # Топ авторов
    authors = {}
    for result in results:
        for author in result.authors:
            authors[author] = authors.get(author, 0) + 1

    print("\nТоп-10 авторов:")
    for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {author}: {count} публикаций")


def example_custom_config():
    """Использование пользовательской конфигурации"""
    print("=" * 80)
    print("Пример 6: Пользовательская конфигурация")
    print("=" * 80)

    # Создание пользовательской конфигурации
    custom_config = {
        "max_results": 10,
        "min_year": 1914,
        "max_year": 1918,
        "databases": ["crossref", "semantic_scholar"]
    }

    # Сохранение конфигурации
    with open("custom_config.json", 'w', encoding='utf-8') as f:
        json.dump(custom_config, f, indent=2)

    # Использование конфигурации
    agent = ScientificHistoryAgent(config_path="custom_config.json")
    results = agent.search("Первая мировая война")

    print(f"\nПоиск с ограничением 1914-1918 годов")
    print(f"Найдено {len(results)} источников\n")

    for result in results[:5]:
        print(f"- {result.title} ({result.year})")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("SCIENTIFIC HISTORY AGENT - ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("=" * 80 + "\n")

    # Запуск примеров
    example_basic_search()
    print("\n" * 2)

    example_advanced_search()
    print("\n" * 2)

    example_multiple_queries()
    print("\n" * 2)

    example_filter_by_database()
    print("\n" * 2)

    example_analysis()
    print("\n" * 2)

    example_custom_config()

    print("\n" + "=" * 80)
    print("Все примеры выполнены!")
    print("=" * 80 + "\n")
