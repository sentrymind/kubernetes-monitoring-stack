# Запуск Scientific History Agent на смартфоне

## 🌐 Вариант 1: Веб-интерфейс (САМЫЙ ПРОСТОЙ!)

### Для любого смартфона (Android/iOS)

1. **Откройте файл `mobile_web.html` в браузере:**
   - Скопируйте файл на смартфон
   - Откройте его в Chrome/Safari/Firefox
   - Готово! Можно искать источники

2. **Или разместите на сервере:**
   ```bash
   # На компьютере
   cd agents/scientific-history-agent
   python3 -m http.server 8000
   ```

   Затем на смартфоне откройте: `http://ваш-ip:8000/mobile_web.html`

### Возможности веб-версии:
- ✅ Работает в любом браузере
- ✅ Адаптивный дизайн для мобильных
- ✅ Офлайн режим с демо-данными
- ✅ Примеры запросов одним тапом
- ✅ Красивый интерфейс

---

## 📱 Вариант 2: Termux (Android)

### Установка Termux

1. Установите [Termux из F-Droid](https://f-droid.org/en/packages/com.termux/)
   - НЕ используйте версию из Google Play (устаревшая)

### Настройка

```bash
# В Termux выполните:

# 1. Обновление пакетов
pkg update && pkg upgrade

# 2. Установка Python
pkg install python

# 3. Установка git
pkg install git

# 4. Клонирование репозитория
git clone https://github.com/sentrymind/kubernetes-monitoring-stack.git
cd kubernetes-monitoring-stack/agents/scientific-history-agent

# 5. Установка зависимостей
pip install requests

# 6. Запуск агента!
python scientific_history_agent.py "Первая мировая война"
```

### Запуск офлайн демо

```bash
cd kubernetes-monitoring-stack/agents/scientific-history-agent
python demo_offline.py
```

### Запуск тестов

```bash
python test_agent.py
```

### Полезные команды Termux

```bash
# Просмотр результатов
cat demo_results.md

# Редактирование конфигурации
nano config.json

# Выход из Termux
exit
```

---

## 🍎 Вариант 3: iOS (Pythonista/a-Shell)

### Pythonista (платное приложение)

1. Установите [Pythonista](https://apps.apple.com/app/pythonista-3/id1085978097)

2. Создайте новый скрипт и скопируйте код из `scientific_history_agent.py`

3. Или используйте встроенный браузер для открытия `mobile_web.html`

### a-Shell (бесплатное)

1. Установите [a-Shell](https://apps.apple.com/app/a-shell/id1473805438)

2. В a-Shell:
```bash
# Установка пакетов
pip install requests

# Скачивание агента
curl -O https://raw.githubusercontent.com/sentrymind/kubernetes-monitoring-stack/main/agents/scientific-history-agent/scientific_history_agent.py

# Запуск
python scientific_history_agent.py "World War"
```

---

## 🌍 Вариант 4: Удаленный доступ через REST API

Если у вас есть компьютер или сервер:

### На компьютере создайте простой API:

```python
# api_server.py
from flask import Flask, request, jsonify
from scientific_history_agent import ScientificHistoryAgent

app = Flask(__name__)
agent = ScientificHistoryAgent()

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '')
    results = agent.search(query)
    return jsonify([{
        'title': r.title,
        'authors': r.authors,
        'year': r.year,
        'url': r.url,
        'abstract': r.abstract,
        'database': r.database
    } for r in results])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Установка и запуск:

```bash
pip install flask
python api_server.py
```

### Использование на смартфоне:

В любом HTTP клиенте (Postman, Insomnia) или через curl в Termux:

```bash
curl -X POST http://ваш-ip:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Первая мировая война"}'
```

---

## 📊 Сравнение вариантов

| Вариант | Сложность | Офлайн | Скорость | Рекомендация |
|---------|-----------|--------|----------|--------------|
| Веб-интерфейс | ⭐ Легко | ✅ Да | ⚡ Мгновенно | ✅ Лучший для начала |
| Termux (Android) | ⭐⭐ Средне | ✅ Да | ⚡⚡ Быстро | ✅ Полный функционал |
| iOS (a-Shell) | ⭐⭐ Средне | ✅ Да | ⚡⚡ Быстро | ✅ Хороший вариант |
| REST API | ⭐⭐⭐ Сложно | ❌ Нет | ⚡⚡⚡ Зависит от сети | Для продвинутых |

---

## 🎯 Рекомендуемый путь

### Для быстрой проверки:
1. Откройте `mobile_web.html` в браузере смартфона
2. Попробуйте готовые примеры
3. Введите свой запрос

### Для полноценной работы:
1. Установите Termux (Android) или a-Shell (iOS)
2. Клонируйте репозиторий
3. Запустите `python demo_offline.py`

---

## 💡 Советы для мобильных устройств

### Экономия батареи:
- Используйте офлайн демо вместо реальных API запросов
- Закрывайте Termux после использования

### Быстрый доступ:
- Добавьте `mobile_web.html` в закладки браузера
- Создайте ярлык на домашнем экране

### Работа с файлами:
- Используйте файловый менеджер для доступа к результатам
- В Termux файлы находятся в `/data/data/com.termux/files/home/`

---

## 🆘 Устранение проблем

### Веб-интерфейс не открывается
- Убедитесь, что файл `mobile_web.html` загружен полностью
- Попробуйте другой браузер

### Termux: "command not found"
```bash
pkg update
pkg install python
```

### iOS: "Module not found"
```bash
pip install requests
```

### Медленная работа
- Используйте офлайн демо: `python demo_offline.py`
- Уменьшите `max_results` в конфигурации

---

## 📸 Скриншоты работы

Веб-интерфейс выглядит так:
- Красивый градиентный дизайн
- Большие кнопки для удобства
- Адаптивная верстка
- Примеры одним тапом

---

## 🎓 Учебные материалы

### Для начинающих:
1. Начните с веб-интерфейса
2. Попробуйте готовые примеры
3. Изучите результаты

### Для продвинутых:
1. Установите Termux
2. Изучите код агента
3. Модифицируйте под свои нужды

---

## 🔗 Полезные ссылки

- [Termux Wiki](https://wiki.termux.com/)
- [a-Shell для iOS](https://holzschu.github.io/a-Shell_iOS/)
- [Pythonista документация](http://omz-software.com/pythonista/docs/)

---

**Выберите наиболее удобный для вас способ и начните использовать Scientific History Agent прямо на смартфоне! 📱🚀**
