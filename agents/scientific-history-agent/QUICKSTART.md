# Быстрый запуск Scientific History Agent

## Вариант 1: Интерактивное демо (РЕКОМЕНДУЕТСЯ)

Самый простой способ попробовать агента:

```bash
cd agents/scientific-history-agent
python3 demo.py
```

Демо автоматически:
- Установит минимальные зависимости
- Предложит выбрать готовый запрос или ввести свой
- Покажет результаты в красивом формате
- Предложит сохранить результаты

## Вариант 2: Автоматический Quick Start

```bash
cd agents/scientific-history-agent
./quick_start.sh
```

Скрипт:
- Проверит установку Python и pip
- Установит все зависимости
- Выполнит демо-поиск "Первая мировая война"
- Сохранит результаты в demo_results.md

## Вариант 3: Ручной запуск

### Шаг 1: Установка зависимостей

```bash
cd agents/scientific-history-agent
pip3 install requests
```

### Шаг 2: Запуск поиска

```bash
python3 scientific_history_agent.py "Революция 1917 года"
```

### Шаг 3: Сохранение результатов

```bash
python3 scientific_history_agent.py "Холодная война" --output results.md --format markdown
```

## Вариант 4: Тестирование

Проверить работу агента без интернета:

```bash
python3 test_agent.py
```

Запустит 7 базовых тестов:
- Инициализация агента
- Загрузка конфигурации
- Улучшение запросов
- Создание результатов
- Фильтрация
- Экспорт в JSON
- Экспорт в Markdown

## Вариант 5: Примеры использования

Посмотреть все возможности агента:

```bash
python3 example_usage.py
```

Запустит 6 примеров:
1. Базовый поиск
2. Расширенный поиск с экспортом
3. Множественные запросы
4. Фильтрация по базе данных
5. Анализ результатов
6. Пользовательская конфигурация

## Частые вопросы

### Нужны ли API ключи?

Нет! Агент работает без API ключей, используя CrossRef API (бесплатный, без регистрации).

Опционально можно добавить ключи для:
- Semantic Scholar (больше результатов)
- CORE (доступ к полным текстам)

### Как добавить API ключи?

```bash
# Скопируйте пример
cp .env.example .env

# Отредактируйте .env и добавьте ключи
nano .env
```

### Что делать, если нет результатов?

1. Проверьте интернет-соединение
2. Используйте более общие запросы
3. Проверьте логи на ошибки

### Как изменить период поиска?

Отредактируйте config.json:

```json
{
  "min_year": 1914,
  "max_year": 1918
}
```

### Как увеличить количество результатов?

```bash
python3 scientific_history_agent.py "запрос" --max-results 100
```

Или в config.json:

```json
{
  "max_results": 100
}
```

## Примеры запросов

### История войн
```bash
python3 scientific_history_agent.py "Первая мировая война"
python3 scientific_history_agent.py "Вторая мировая война"
python3 scientific_history_agent.py "Холодная война"
```

### Политическая история
```bash
python3 scientific_history_agent.py "Революция 1917 года"
python3 scientific_history_agent.py "Формирование СССР"
python3 scientific_history_agent.py "Распад колониальных империй"
```

### Экономическая история
```bash
python3 scientific_history_agent.py "Великая депрессия"
python3 scientific_history_agent.py "План Маршалла"
python3 scientific_history_agent.py "Индустриализация"
```

### Культурная история
```bash
python3 scientific_history_agent.py "Модернизм в искусстве"
python3 scientific_history_agent.py "История кинематографа"
python3 scientific_history_agent.py "Развитие музыки"
```

### Технологическая история
```bash
python3 scientific_history_agent.py "Развитие авиации"
python3 scientific_history_agent.py "Космическая гонка"
python3 scientific_history_agent.py "История радио"
```

## Форматы экспорта

### Markdown (для чтения)
```bash
python3 scientific_history_agent.py "запрос" --output results.md --format markdown
```

### JSON (для обработки)
```bash
python3 scientific_history_agent.py "запрос" --output results.json --format json
```

### CSV (для Excel)
```bash
python3 scientific_history_agent.py "запрос" --output results.csv --format csv
```

## Устранение проблем

### ModuleNotFoundError: No module named 'requests'

```bash
pip3 install requests
```

### TimeoutError или ConnectionError

1. Проверьте интернет
2. Попробуйте позже (API может быть недоступен)
3. Увеличьте timeout в коде

### Нет результатов

Агент автоматически добавляет контекст XX века. Если результатов нет:
- Используйте более общие запросы
- Проверьте правильность написания
- Попробуйте на английском языке

## Дополнительная помощь

- Полная документация: `README.md`
- Примеры: `example_usage.py`
- Тесты: `test_agent.py`
- Конфигурация: `config.json`

---

Выберите любой вариант и начните работу с агентом прямо сейчас!
