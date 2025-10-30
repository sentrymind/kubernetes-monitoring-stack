#!/usr/bin/env python3
"""
Scientific History Agent - Агент для поиска информации в научных источниках
по истории Двадцатого века.

Этот агент интегрируется с различными научными базами данных для поиска
академических статей, книг и исследований по истории XX века.
"""

import os
import json
import logging
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from urllib.parse import quote

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Результат поиска в научных источниках"""
    title: str
    authors: List[str]
    year: Optional[int]
    source: str
    abstract: str
    url: str
    relevance_score: float
    database: str


class ScientificHistoryAgent:
    """
    Агент для поиска информации в научных источниках по истории XX века.

    Поддерживаемые базы данных:
    - CrossRef (научные публикации)
    - arXiv (препринты)
    - Core.ac.uk (открытый доступ к научным работам)
    - Semantic Scholar (AI-powered научный поиск)
    """

    HISTORY_KEYWORDS = [
        "история", "history", "исторический", "historical",
        "XX век", "20th century", "двадцатый век"
    ]

    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация агента.

        Args:
            config_path: Путь к конфигурационному файлу
        """
        self.config = self._load_config(config_path)
        self.results_cache = []
        logger.info("Scientific History Agent инициализирован")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Загрузка конфигурации"""
        default_config = {
            "max_results": 50,
            "min_year": 1900,
            "max_year": 1999,
            "languages": ["ru", "en"],
            "databases": ["crossref", "semantic_scholar", "core"],
            "api_keys": {
                "semantic_scholar": os.getenv("SEMANTIC_SCHOLAR_API_KEY"),
                "core": os.getenv("CORE_API_KEY")
            }
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def search(self, query: str) -> List[SearchResult]:
        """
        Поиск информации по запросу во всех настроенных базах данных.

        Args:
            query: Поисковый запрос

        Returns:
            Список результатов поиска
        """
        logger.info(f"Начинаю поиск по запросу: '{query}'")

        # Добавляем контекст истории XX века к запросу
        enhanced_query = self._enhance_query(query)

        all_results = []

        if "crossref" in self.config["databases"]:
            all_results.extend(self._search_crossref(enhanced_query))

        if "semantic_scholar" in self.config["databases"]:
            all_results.extend(self._search_semantic_scholar(enhanced_query))

        if "core" in self.config["databases"]:
            all_results.extend(self._search_core(enhanced_query))

        # Фильтрация и сортировка результатов
        filtered_results = self._filter_results(all_results)
        sorted_results = sorted(
            filtered_results,
            key=lambda x: x.relevance_score,
            reverse=True
        )

        self.results_cache = sorted_results[:self.config["max_results"]]
        logger.info(f"Найдено {len(self.results_cache)} релевантных результатов")

        return self.results_cache

    def _enhance_query(self, query: str) -> str:
        """Улучшение запроса с учетом контекста истории XX века"""
        if not any(keyword in query.lower() for keyword in self.HISTORY_KEYWORDS):
            query += " история XX века history 20th century"
        return query

    def _search_crossref(self, query: str) -> List[SearchResult]:
        """Поиск в базе данных CrossRef"""
        logger.info("Поиск в CrossRef...")
        results = []

        try:
            url = "https://api.crossref.org/works"
            params = {
                "query": query,
                "filter": f"from-pub-date:{self.config['min_year']},until-pub-date:{self.config['max_year']}",
                "rows": 20,
                "select": "title,author,published,abstract,URL,subject"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for item in data.get("message", {}).get("items", []):
                try:
                    # Извлекаем год публикации
                    pub_date = item.get("published", {}).get("date-parts", [[None]])[0]
                    year = pub_date[0] if pub_date else None

                    # Проверяем, что это XX век
                    if year and (year < 1900 or year > 1999):
                        continue

                    result = SearchResult(
                        title=item.get("title", [""])[0],
                        authors=[
                            f"{a.get('given', '')} {a.get('family', '')}"
                            for a in item.get("author", [])
                        ],
                        year=year,
                        source=item.get("container-title", [""])[0],
                        abstract=item.get("abstract", "Аннотация недоступна"),
                        url=item.get("URL", ""),
                        relevance_score=item.get("score", 0.0),
                        database="CrossRef"
                    )
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Ошибка обработки результата CrossRef: {e}")
                    continue

            logger.info(f"Найдено {len(results)} результатов в CrossRef")
        except Exception as e:
            logger.error(f"Ошибка поиска в CrossRef: {e}")

        return results

    def _search_semantic_scholar(self, query: str) -> List[SearchResult]:
        """Поиск в Semantic Scholar"""
        logger.info("Поиск в Semantic Scholar...")
        results = []

        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            headers = {}
            if self.config["api_keys"].get("semantic_scholar"):
                headers["x-api-key"] = self.config["api_keys"]["semantic_scholar"]

            params = {
                "query": query,
                "fields": "title,authors,year,abstract,url,citationCount",
                "limit": 20
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            for item in data.get("data", []):
                try:
                    year = item.get("year")

                    # Проверяем, что это XX век
                    if year and (year < 1900 or year > 1999):
                        continue

                    result = SearchResult(
                        title=item.get("title", ""),
                        authors=[a.get("name", "") for a in item.get("authors", [])],
                        year=year,
                        source="Semantic Scholar",
                        abstract=item.get("abstract", "Аннотация недоступна"),
                        url=item.get("url", ""),
                        relevance_score=float(item.get("citationCount", 0)) / 100.0,
                        database="Semantic Scholar"
                    )
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Ошибка обработки результата Semantic Scholar: {e}")
                    continue

            logger.info(f"Найдено {len(results)} результатов в Semantic Scholar")
        except Exception as e:
            logger.error(f"Ошибка поиска в Semantic Scholar: {e}")

        return results

    def _search_core(self, query: str) -> List[SearchResult]:
        """Поиск в CORE (открытый доступ к научным работам)"""
        logger.info("Поиск в CORE...")
        results = []

        try:
            if not self.config["api_keys"].get("core"):
                logger.warning("API ключ CORE не настроен, пропускаю поиск")
                return results

            url = "https://api.core.ac.uk/v3/search/works"
            headers = {
                "Authorization": f"Bearer {self.config['api_keys']['core']}"
            }

            params = {
                "q": query,
                "limit": 20
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            for item in data.get("results", []):
                try:
                    year = item.get("yearPublished")

                    # Проверяем, что это XX век
                    if year and (year < 1900 or year > 1999):
                        continue

                    result = SearchResult(
                        title=item.get("title", ""),
                        authors=item.get("authors", []),
                        year=year,
                        source=item.get("publisher", "CORE"),
                        abstract=item.get("abstract", "Аннотация недоступна"),
                        url=item.get("downloadUrl", ""),
                        relevance_score=float(item.get("score", 0.0)),
                        database="CORE"
                    )
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Ошибка обработки результата CORE: {e}")
                    continue

            logger.info(f"Найдено {len(results)} результатов в CORE")
        except Exception as e:
            logger.error(f"Ошибка поиска в CORE: {e}")

        return results

    def _filter_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Фильтрация результатов по релевантности"""
        filtered = []

        for result in results:
            # Проверяем год публикации
            if result.year and (result.year < 1900 or result.year > 1999):
                continue

            # Проверяем наличие ключевых слов истории
            title_lower = result.title.lower()
            abstract_lower = result.abstract.lower()

            has_history_keyword = any(
                keyword in title_lower or keyword in abstract_lower
                for keyword in self.HISTORY_KEYWORDS
            )

            if has_history_keyword or result.year:
                filtered.append(result)

        return filtered

    def export_results(self, output_file: str, format: str = "json"):
        """
        Экспорт результатов поиска.

        Args:
            output_file: Путь к файлу для сохранения
            format: Формат экспорта (json, csv, markdown)
        """
        if not self.results_cache:
            logger.warning("Нет результатов для экспорта")
            return

        logger.info(f"Экспорт результатов в {output_file} (формат: {format})")

        if format == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(
                    [asdict(r) for r in self.results_cache],
                    f,
                    ensure_ascii=False,
                    indent=2
                )

        elif format == "markdown":
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# Результаты поиска - История XX века\n\n")
                f.write(f"**Дата поиска:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                f.write(f"**Найдено источников:** {len(self.results_cache)}\n\n")
                f.write("---\n\n")

                for i, result in enumerate(self.results_cache, 1):
                    f.write(f"## {i}. {result.title}\n\n")
                    f.write(f"**Авторы:** {', '.join(result.authors)}\n\n")
                    f.write(f"**Год:** {result.year}\n\n")
                    f.write(f"**Источник:** {result.source}\n\n")
                    f.write(f"**База данных:** {result.database}\n\n")
                    f.write(f"**URL:** {result.url}\n\n")
                    f.write(f"**Аннотация:**\n{result.abstract}\n\n")
                    f.write(f"**Релевантность:** {result.relevance_score:.2f}\n\n")
                    f.write("---\n\n")

        elif format == "csv":
            import csv
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['title', 'authors', 'year', 'source', 'database', 'url', 'relevance_score']
                )
                writer.writeheader()
                for result in self.results_cache:
                    writer.writerow({
                        'title': result.title,
                        'authors': '; '.join(result.authors),
                        'year': result.year,
                        'source': result.source,
                        'database': result.database,
                        'url': result.url,
                        'relevance_score': result.relevance_score
                    })

        logger.info(f"Результаты успешно экспортированы в {output_file}")


def main():
    """Основная функция для запуска агента из командной строки"""
    parser = argparse.ArgumentParser(
        description='Scientific History Agent - Поиск в научных источниках по истории XX века'
    )
    parser.add_argument(
        'query',
        type=str,
        help='Поисковый запрос'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Путь к конфигурационному файлу'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Путь к файлу для сохранения результатов'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'markdown', 'csv'],
        default='markdown',
        help='Формат выходного файла'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=50,
        help='Максимальное количество результатов'
    )

    args = parser.parse_args()

    # Создаем агента
    agent = ScientificHistoryAgent(config_path=args.config)

    # Обновляем конфигурацию из аргументов
    if args.max_results:
        agent.config['max_results'] = args.max_results

    # Выполняем поиск
    results = agent.search(args.query)

    # Выводим результаты
    print(f"\n{'='*80}")
    print(f"Найдено {len(results)} научных источников по запросу: '{args.query}'")
    print(f"{'='*80}\n")

    for i, result in enumerate(results[:10], 1):
        print(f"{i}. {result.title}")
        print(f"   Авторы: {', '.join(result.authors[:3])}")
        print(f"   Год: {result.year}")
        print(f"   База данных: {result.database}")
        print(f"   URL: {result.url}")
        print()

    if len(results) > 10:
        print(f"... и ещё {len(results) - 10} результатов\n")

    # Экспортируем результаты, если указан файл
    if args.output:
        agent.export_results(args.output, format=args.format)
        print(f"Результаты сохранены в {args.output}")


if __name__ == "__main__":
    main()
