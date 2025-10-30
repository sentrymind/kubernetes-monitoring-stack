# Scientific History Agent

Агент для поиска информации в научных источниках по Истории Двадцатого века (XX век, 1900-1999 годы).

## Описание

Scientific History Agent - это специализированный инструмент для поиска и анализа академических источников, сфокусированных на исторических событиях и исследованиях XX века. Агент интегрируется с ведущими научными базами данных и предоставляет структурированные результаты.

### Ключевые возможности

- **Многоисточниковый поиск**: Интеграция с CrossRef, Semantic Scholar, CORE
- **Временная фильтрация**: Автоматический фильтр публикаций по периоду 1900-1999
- **Контекстный поиск**: Автоматическое добавление исторического контекста к запросам
- **Релевантность**: Умная сортировка результатов по релевантности
- **Множественные форматы экспорта**: JSON, Markdown, CSV

### Поддерживаемые базы данных

| База данных | Описание | API ключ |
|-------------|----------|----------|
| **CrossRef** | Крупнейшая база научных публикаций | Не требуется |
| **Semantic Scholar** | AI-powered научный поиск | Опционально |
| **CORE** | Открытый доступ к научным работам | Требуется |

## Установка

### Требования

- Python 3.8+
- pip

### Установка зависимостей

```bash
cd agents/scientific-history-agent
pip install -r requirements.txt
```

### Настройка API ключей (опционально)

Для расширенного функционала создайте файл `.env`:

```bash
# .env
SEMANTIC_SCHOLAR_API_KEY=ваш_ключ_здесь
CORE_API_KEY=ваш_ключ_здесь
```

#### Получение API ключей

**Semantic Scholar:**
- Регистрация: https://www.semanticscholar.org/product/api
- Бесплатный тариф: 5000 запросов в день

**CORE:**
- Регистрация: https://core.ac.uk/services/api
- Бесплатный тариф: 10000 запросов в месяц

## Использование

### Базовый поиск

```bash
python scientific_history_agent.py "Первая мировая война"
```

### Поиск с сохранением результатов

```bash
python scientific_history_agent.py "Революция 1917 года" \
  --output results.md \
  --format markdown
```

### Использование пользовательской конфигурации

```bash
python scientific_history_agent.py "Холодная война" \
  --config my_config.json \
  --max-results 100
```

### Примеры запросов

```bash
# История технологий XX века
python scientific_history_agent.py "развитие авиации"

# Политическая история
python scientific_history_agent.py "формирование СССР"

# Культурная история
python scientific_history_agent.py "модернизм в искусстве"

# Социальная история
python scientific_history_agent.py "урбанизация XX века"

# Экономическая история
python scientific_history_agent.py "Великая депрессия"
```

## Конфигурация

Файл `config.json` содержит настройки агента:

```json
{
  "max_results": 50,
  "min_year": 1900,
  "max_year": 1999,
  "languages": ["ru", "en"],
  "databases": ["crossref", "semantic_scholar", "core"],
  "api_keys": {
    "semantic_scholar": "",
    "core": ""
  }
}
```

### Параметры конфигурации

| Параметр | Описание | Значение по умолчанию |
|----------|----------|-----------------------|
| `max_results` | Максимальное количество результатов | 50 |
| `min_year` | Минимальный год публикации | 1900 |
| `max_year` | Максимальный год публикации | 1999 |
| `languages` | Языки поиска | ["ru", "en"] |
| `databases` | Активные базы данных | Все |

## Использование как библиотеки

```python
from scientific_history_agent import ScientificHistoryAgent

# Создание агента
agent = ScientificHistoryAgent(config_path="config.json")

# Поиск
results = agent.search("Вторая мировая война")

# Обработка результатов
for result in results:
    print(f"Название: {result.title}")
    print(f"Авторы: {', '.join(result.authors)}")
    print(f"Год: {result.year}")
    print(f"База данных: {result.database}")
    print(f"URL: {result.url}")
    print()

# Экспорт результатов
agent.export_results("output.json", format="json")
agent.export_results("output.md", format="markdown")
agent.export_results("output.csv", format="csv")
```

## Форматы экспорта

### JSON
Структурированные данные для программной обработки.

```bash
python scientific_history_agent.py "запрос" --output results.json --format json
```

### Markdown
Читаемый формат с полной информацией о каждом источнике.

```bash
python scientific_history_agent.py "запрос" --output results.md --format markdown
```

### CSV
Табличный формат для анализа в Excel или других инструментах.

```bash
python scientific_history_agent.py "запрос" --output results.csv --format csv
```

## Расширенные возможности

### Фильтрация результатов

Агент автоматически фильтрует результаты по:
- Временному периоду (1900-1999)
- Ключевым словам истории
- Релевантности к запросу

### Улучшение запросов

Агент автоматически добавляет контекст к запросам:
- "Первая мировая война" → "Первая мировая война история XX века history 20th century"

### Кэширование результатов

Результаты поиска кэшируются в памяти агента для быстрого доступа.

## Интеграция с другими инструментами

### Jupyter Notebook

```python
import sys
sys.path.append('/path/to/agents/scientific-history-agent')

from scientific_history_agent import ScientificHistoryAgent
import pandas as pd

agent = ScientificHistoryAgent()
results = agent.search("Холодная война")

# Конвертация в DataFrame для анализа
df = pd.DataFrame([vars(r) for r in results])
df.head()
```

### REST API обертка

```python
from flask import Flask, jsonify, request
from scientific_history_agent import ScientificHistoryAgent

app = Flask(__name__)
agent = ScientificHistoryAgent()

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    results = agent.search(query)
    return jsonify([vars(r) for r in results])

if __name__ == '__main__':
    app.run(port=5000)
```

## Мониторинг и логирование

Агент использует стандартный модуль `logging` Python:

```python
import logging

# Настройка уровня логирования
logging.basicConfig(level=logging.DEBUG)

agent = ScientificHistoryAgent()
agent.search("запрос")
```

## Производительность

- **Время поиска**: 2-5 секунд на запрос
- **Количество результатов**: До 50 по умолчанию (настраивается)
- **Использование памяти**: ~50-100 МБ
- **Поддерживаемая нагрузка**: До 100 запросов в минуту

## Ограничения

- Некоторые научные базы данных требуют API ключи
- Результаты зависят от доступности внешних API
- Временные ограничения rate limits различных сервисов
- Полнотекстовый доступ не всегда доступен

## Устранение проблем

### Нет результатов

1. Проверьте подключение к интернету
2. Убедитесь, что запрос содержит исторический контекст
3. Проверьте логи на предмет ошибок API

### Ошибки API

```bash
# Проверка доступности API
curl https://api.crossref.org/works?query=history

# Проверка API ключей
echo $SEMANTIC_SCHOLAR_API_KEY
echo $CORE_API_KEY
```

### Медленный поиск

1. Уменьшите `max_results` в конфигурации
2. Отключите неиспользуемые базы данных
3. Используйте более специфичные запросы

## Примеры результатов

```markdown
## 1. The Origins of the First World War

**Авторы:** James Joll, Gordon Martel

**Год:** 1992

**Источник:** Cambridge University Press

**База данных:** CrossRef

**URL:** https://doi.org/10.1017/...

**Аннотация:**
This book examines the origins of the First World War,
exploring the complex web of alliances, militarism, and
nationalism that led to the conflict...

**Релевантность:** 0.95
```

## Содействие

Приветствуются вклады в развитие агента:

1. Добавление новых научных баз данных
2. Улучшение алгоритмов фильтрации
3. Расширение функционала экспорта
4. Оптимизация производительности

## Лицензия

MIT License - см. файл LICENSE в корне проекта.

## Контакты и поддержка

- GitHub Issues: для сообщений об ошибках
- Документация: этот README
- Примеры использования: см. папку `examples/`

## История изменений

### v1.0.0 (2025-10-30)
- Первый релиз
- Интеграция с CrossRef, Semantic Scholar, CORE
- Поддержка экспорта в JSON, Markdown, CSV
- Автоматическая фильтрация по XX веку
- Многоязычный поиск (RU, EN)

---

**Создано для исследователей истории XX века**
