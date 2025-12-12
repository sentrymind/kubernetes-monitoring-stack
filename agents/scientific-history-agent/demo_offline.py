#!/usr/bin/env python3
"""
Офлайн демо Scientific History Agent
Использует предзаполненные данные для демонстрации работы
"""

from scientific_history_agent import SearchResult
import json

def print_header(text):
    """Печать заголовка"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_result(i, result):
    """Печать одного результата"""
    print(f"{i}. 📄 {result.title}")
    if result.authors:
        authors = ", ".join(result.authors[:2])
        if len(result.authors) > 2:
            authors += f" и др."
        print(f"   👤 Авторы: {authors}")
    if result.year:
        print(f"   📅 Год: {result.year}")
    print(f"   🗄️  База: {result.database}")
    if result.url:
        print(f"   🔗 URL: {result.url}")
    if result.abstract and result.abstract != "Аннотация недоступна":
        abstract = result.abstract[:150] + "..." if len(result.abstract) > 150 else result.abstract
        print(f"   📝 Аннотация: {abstract}")
    print(f"   ⭐ Релевантность: {result.relevance_score:.2f}")
    print()

def get_demo_results():
    """Получение демо-данных"""
    return [
        SearchResult(
            title="The Origins of the First World War",
            authors=["James Joll", "Gordon Martel"],
            year=1992,
            source="Cambridge University Press",
            abstract="Это классическое исследование рассматривает причины Первой мировой войны, анализируя сложную сеть союзов, милитаризма и национализма, которые привели к конфликту 1914-1918 годов.",
            url="https://doi.org/10.1017/CBO9780511608568",
            relevance_score=0.95,
            database="CrossRef"
        ),
        SearchResult(
            title="Russia in Revolution: An Empire in Crisis, 1890 to 1928",
            authors=["S. A. Smith"],
            year=1917,
            source="Oxford University Press",
            abstract="Всестороннее исследование российской революции, охватывающее период от падения царизма до установления сталинского режима.",
            url="https://doi.org/10.1093/acprof:oso/9780199214426.001.0001",
            relevance_score=0.93,
            database="Semantic Scholar"
        ),
        SearchResult(
            title="The Great Depression: An International Disaster of Perverse Economic Policies",
            authors=["Thomas E. Hall", "J. David Ferguson"],
            year=1998,
            source="University of Michigan Press",
            abstract="Анализ экономических политик, которые привели к Великой депрессии 1929-1939 годов и их международных последствий.",
            url="https://doi.org/10.3998/mpub.15738",
            relevance_score=0.91,
            database="CrossRef"
        ),
        SearchResult(
            title="The Cold War: A New History",
            authors=["John Lewis Gaddis"],
            year=1947,
            source="Penguin Press",
            abstract="Новый взгляд на Холодную войну, основанный на недавно рассекреченных архивных материалах из США, России и Китая.",
            url="https://www.penguinrandomhouse.com/books/301359/",
            relevance_score=0.89,
            database="Semantic Scholar"
        ),
        SearchResult(
            title="Modernism: A Very Short Introduction",
            authors=["Christopher Butler"],
            year=1920,
            source="Oxford University Press",
            abstract="Краткое введение в модернизм в искусстве, литературе и музыке XX века, рассматривающее ключевые движения и фигуры.",
            url="https://doi.org/10.1093/actrade/9780192804419.001.0001",
            relevance_score=0.87,
            database="CrossRef"
        ),
        SearchResult(
            title="A History of the World in the Twentieth Century",
            authors=["Martin Gilbert"],
            year=1988,
            source="William Morrow Paperbacks",
            abstract="Всеобъемлющая история ключевых событий, войн, революций и социальных изменений в XX веке.",
            url="https://www.harpercollins.com/",
            relevance_score=0.85,
            database="CrossRef"
        ),
        SearchResult(
            title="The Age of Extremes: The Short Twentieth Century, 1914-1991",
            authors=["Eric Hobsbawm"],
            year=1994,
            source="Pantheon Books",
            abstract="Исторический анализ 'короткого двадцатого века' от начала Первой мировой войны до распада Советского Союза.",
            url="https://www.penguinrandomhouse.com/books/147870/",
            relevance_score=0.92,
            database="Semantic Scholar"
        ),
        SearchResult(
            title="The Second World War",
            authors=["Antony Beevor"],
            year=1939,
            source="Little, Brown and Company",
            abstract="Всесторонний рассказ о Второй мировой войне, охватывающий все театры военных действий с использованием архивных материалов.",
            url="https://www.littlebrown.com/",
            relevance_score=0.94,
            database="CrossRef"
        ),
        SearchResult(
            title="The Spanish Civil War",
            authors=["Hugh Thomas"],
            year=1977,
            source="Harper & Row",
            abstract="Подробная история гражданской войны в Испании 1936-1939 годов, предшествовавшей Второй мировой войне.",
            url="https://www.harpercollins.com/",
            relevance_score=0.82,
            database="Semantic Scholar"
        ),
        SearchResult(
            title="Women's Suffrage and the First World War",
            authors=["Angela K. Smith"],
            year=1918,
            source="Palgrave Macmillan",
            abstract="Исследование роли Первой мировой войны в движении за избирательные права женщин в Великобритании.",
            url="https://doi.org/10.1057/9780230234567",
            relevance_score=0.80,
            database="CrossRef"
        )
    ]

def main():
    """Главная функция демо"""
    print_header("🤖 Scientific History Agent - ОФЛАЙН ДЕМО")

    print("ВНИМАНИЕ: Это офлайн демо с предзаполненными данными.")
    print("Для реальных поисков используйте: python3 scientific_history_agent.py")
    print()
    print("Этот агент ищет научные источники по истории XX века (1900-1999)")
    print()

    # Получаем демо-результаты
    results = get_demo_results()

    print(f"✅ Демо содержит {len(results)} примеров научных источников\n")
    print("-" * 70)

    for i, result in enumerate(results, 1):
        print_result(i, result)

    # Статистика
    print_header("📊 Статистика демо-данных")

    # По годам
    years = {}
    for r in results:
        if r.year:
            decade = (r.year // 10) * 10
            years[decade] = years.get(decade, 0) + 1

    print("Распределение по десятилетиям:")
    for decade in sorted(years.keys()):
        bar = "█" * years[decade]
        print(f"  {decade}s: {bar} ({years[decade]})")
    print()

    # По базам данных
    databases = {}
    for r in results:
        databases[r.database] = databases.get(r.database, 0) + 1

    print("Распределение по базам данных:")
    for db, count in databases.items():
        print(f"  {db}: {count} источников")
    print()

    # Экспорт
    print_header("💾 Экспорт демо-данных")

    # JSON
    with open("demo_results.json", 'w', encoding='utf-8') as f:
        json.dump(
            [vars(r) for r in results],
            f,
            ensure_ascii=False,
            indent=2
        )
    print("✅ Сохранено в demo_results.json")

    # Markdown
    with open("demo_results.md", 'w', encoding='utf-8') as f:
        f.write("# Демо результаты - Scientific History Agent\n\n")
        f.write(f"**Количество источников:** {len(results)}\n\n")
        f.write("---\n\n")

        for i, r in enumerate(results, 1):
            f.write(f"## {i}. {r.title}\n\n")
            f.write(f"**Авторы:** {', '.join(r.authors)}\n\n")
            f.write(f"**Год:** {r.year}\n\n")
            f.write(f"**Источник:** {r.source}\n\n")
            f.write(f"**База данных:** {r.database}\n\n")
            f.write(f"**URL:** {r.url}\n\n")
            f.write(f"**Аннотация:**\n{r.abstract}\n\n")
            f.write(f"**Релевантность:** {r.relevance_score:.2f}\n\n")
            f.write("---\n\n")

    print("✅ Сохранено в demo_results.md")

    print()
    print_header("✨ Демо завершено!")
    print("Файлы с результатами:")
    print("  - demo_results.json (JSON формат)")
    print("  - demo_results.md (Markdown формат)")
    print()
    print("Для реальных поисков:")
    print("  python3 scientific_history_agent.py \"ваш запрос\" --output results.md")
    print()

if __name__ == "__main__":
    main()
