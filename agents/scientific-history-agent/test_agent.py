#!/usr/bin/env python3
"""
Простые тесты для Scientific History Agent
"""

import sys
import os
from scientific_history_agent import ScientificHistoryAgent, SearchResult


def test_agent_initialization():
    """Тест инициализации агента"""
    print("Тест 1: Инициализация агента...", end=" ")
    try:
        agent = ScientificHistoryAgent()
        assert agent is not None
        assert agent.config is not None
        assert agent.config['min_year'] == 1900
        assert agent.config['max_year'] == 1999
        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_config_loading():
    """Тест загрузки конфигурации"""
    print("Тест 2: Загрузка конфигурации...", end=" ")
    try:
        agent = ScientificHistoryAgent(config_path="config.json")
        assert agent.config['max_results'] == 50
        assert 'crossref' in agent.config['databases']
        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_query_enhancement():
    """Тест улучшения запросов"""
    print("Тест 3: Улучшение запросов...", end=" ")
    try:
        agent = ScientificHistoryAgent()

        # Запрос без исторического контекста
        enhanced = agent._enhance_query("Первая мировая война")
        assert "история" in enhanced or "history" in enhanced

        # Запрос с историческим контекстом
        enhanced2 = agent._enhance_query("История Второй мировой войны")
        assert "История" in enhanced2

        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_search_result_creation():
    """Тест создания результата поиска"""
    print("Тест 4: Создание результата поиска...", end=" ")
    try:
        result = SearchResult(
            title="Test Title",
            authors=["Author 1", "Author 2"],
            year=1945,
            source="Test Source",
            abstract="Test abstract",
            url="https://example.com",
            relevance_score=0.95,
            database="TestDB"
        )
        assert result.title == "Test Title"
        assert len(result.authors) == 2
        assert result.year == 1945
        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_result_filtering():
    """Тест фильтрации результатов"""
    print("Тест 5: Фильтрация результатов...", end=" ")
    try:
        agent = ScientificHistoryAgent()

        # Создаем тестовые результаты
        results = [
            SearchResult(
                title="История XX века",
                authors=["Test"],
                year=1950,
                source="Test",
                abstract="Исторический анализ",
                url="",
                relevance_score=0.9,
                database="Test"
            ),
            SearchResult(
                title="Modern Study",
                authors=["Test"],
                year=2020,  # Не XX век
                source="Test",
                abstract="Contemporary analysis",
                url="",
                relevance_score=0.8,
                database="Test"
            ),
            SearchResult(
                title="Ancient History",
                authors=["Test"],
                year=1800,  # Не XX век
                source="Test",
                abstract="Old history",
                url="",
                relevance_score=0.7,
                database="Test"
            )
        ]

        filtered = agent._filter_results(results)

        # Должен остаться только один результат (1950 год)
        assert len(filtered) == 1
        assert filtered[0].year == 1950

        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_export_json():
    """Тест экспорта в JSON"""
    print("Тест 6: Экспорт в JSON...", end=" ")
    try:
        agent = ScientificHistoryAgent()

        # Создаем тестовый результат
        agent.results_cache = [
            SearchResult(
                title="Test",
                authors=["Author"],
                year=1945,
                source="Source",
                abstract="Abstract",
                url="https://test.com",
                relevance_score=0.9,
                database="TestDB"
            )
        ]

        # Экспорт
        test_file = "test_export.json"
        agent.export_results(test_file, format="json")

        # Проверка
        assert os.path.exists(test_file)

        # Очистка
        os.remove(test_file)

        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_export_markdown():
    """Тест экспорта в Markdown"""
    print("Тест 7: Экспорт в Markdown...", end=" ")
    try:
        agent = ScientificHistoryAgent()

        # Создаем тестовый результат
        agent.results_cache = [
            SearchResult(
                title="Test Title",
                authors=["Author 1"],
                year=1945,
                source="Test Source",
                abstract="Test abstract",
                url="https://test.com",
                relevance_score=0.9,
                database="TestDB"
            )
        ]

        # Экспорт
        test_file = "test_export.md"
        agent.export_results(test_file, format="markdown")

        # Проверка
        assert os.path.exists(test_file)

        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test Title" in content
            assert "1945" in content

        # Очистка
        os.remove(test_file)

        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("SCIENTIFIC HISTORY AGENT - ТЕСТЫ")
    print("=" * 60)
    print()

    tests = [
        test_agent_initialization,
        test_config_loading,
        test_query_enhancement,
        test_search_result_creation,
        test_result_filtering,
        test_export_json,
        test_export_markdown
    ]

    passed = 0
    failed = 0

    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1

    print()
    print("=" * 60)
    print(f"РЕЗУЛЬТАТЫ: {passed} PASSED, {failed} FAILED")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
