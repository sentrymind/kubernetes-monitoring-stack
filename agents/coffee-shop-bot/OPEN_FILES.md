# 📂 Как открыть и посмотреть файлы бота

## 📍 Где находятся файлы

**Полный путь:**
```
/home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot/
```

---

## 💻 Способы открыть файлы

### 1️⃣ В терминале (командная строка)

#### Перейти в папку:
```bash
cd /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot
```

#### Посмотреть список файлов:
```bash
ls -lh
```

#### Открыть файл в редакторе:
```bash
# Nano (простой редактор)
nano coffee_bot.py

# Vim (продвинутый редактор)
vim coffee_bot.py

# Просто посмотреть содержимое
cat coffee_bot.py

# Посмотреть с прокруткой
less coffee_bot.py
```

---

### 2️⃣ Файловый менеджер (GUI)

#### Linux:
```bash
# Nautilus (Ubuntu/GNOME)
nautilus /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot

# Dolphin (KDE)
dolphin /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot

# Thunar (XFCE)
thunar /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot

# Или просто
xdg-open /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot
```

#### macOS:
```bash
open /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot
```

#### Windows (WSL):
```bash
explorer.exe /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot
```

---

### 3️⃣ VS Code

#### Открыть папку в VS Code:
```bash
cd /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot
code .
```

#### Или открыть конкретный файл:
```bash
code coffee_bot.py
```

---

### 4️⃣ GitHub

Если файлы уже запушены на GitHub:

1. Откройте: https://github.com/sentrymind/kubernetes-monitoring-stack
2. Перейдите в: `agents` → `coffee-shop-bot`
3. Кликните на любой файл для просмотра

**Ветка:** `claude/scientific-sources-agent-011CUd7vAk9s6juvMG5bBi3H`

---

### 5️⃣ Через браузер (локально)

Для HTML файлов (например, для агента истории):

```bash
# Просто откройте в браузере
firefox mobile_web.html
# или
google-chrome mobile_web.html
```

---

### 6️⃣ На смартфоне (Android)

#### Через Termux:
```bash
# Установите Termux File Manager
pkg install termux-tools

# Откройте файл
termux-open /data/data/com.termux/files/home/kubernetes-monitoring-stack/agents/coffee-shop-bot/
```

#### Через обычный файловый менеджер:
1. Используйте Total Commander или ES File Explorer
2. Перейдите в папку с репозиторием
3. Найдите `agents/coffee-shop-bot/`

---

## 📄 Какие файлы смотреть

### Основные файлы:

**1. coffee_bot.py** - Главный код бота
```bash
cat coffee_bot.py | head -50  # Первые 50 строк
```

**2. menu_data.py** - Ваше меню
```bash
cat menu_data.py
```

**3. README.md** - Документация
```bash
cat README.md | less  # С прокруткой
```

**4. QUICKSTART.md** - Быстрый старт
```bash
cat QUICKSTART.md
```

---

## 🔍 Поиск по файлам

### Найти все файлы Python:
```bash
find . -name "*.py"
```

### Найти строку в файлах:
```bash
grep -r "МЕНЮ" .
```

### Посмотреть размер файлов:
```bash
du -sh *
```

---

## ✏️ Редактирование файлов

### Nano (самый простой):
```bash
nano coffee_bot.py

# Сохранить: Ctrl+O, Enter
# Выйти: Ctrl+X
```

### Vim:
```bash
vim coffee_bot.py

# Вставить текст: i
# Сохранить и выйти: :wq
# Выйти без сохранения: :q!
```

### VS Code:
```bash
code coffee_bot.py
```

---

## 📦 Скопировать файлы

### На другой компьютер:
```bash
# Архивировать
tar -czf coffee-bot.tar.gz /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot/

# Или zip
zip -r coffee-bot.zip /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot/
```

### На USB флешку:
```bash
cp -r /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot/ /media/usb/
```

### Через SCP (на другой сервер):
```bash
scp -r /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot/ user@server:/path/
```

---

## 🌐 Открыть в онлайн редакторе

### GitHub Codespaces:
1. Откройте репозиторий на GitHub
2. Нажмите `.` (точку) на клавиатуре
3. Откроется VS Code в браузере!

### repl.it:
1. Перейдите на https://replit.com
2. Импортируйте из GitHub
3. Редактируйте онлайн

---

## 💡 Полезные команды

### Посмотреть структуру проекта:
```bash
tree /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot/
# или
ls -R /home/user/kubernetes-monitoring-stack/agents/coffee-shop-bot/
```

### Посчитать строки кода:
```bash
wc -l *.py
```

### Найти TODO в коде:
```bash
grep -n "TODO" *.py
```

### Посмотреть последние изменения:
```bash
git log --oneline
```

---

## 🆘 Не можете найти файлы?

### Поиск по всей системе:
```bash
find / -name "coffee_bot.py" 2>/dev/null
```

### Проверка текущей директории:
```bash
pwd
```

### Вернуться в домашнюю директорию:
```bash
cd ~
```

---

## 📱 Поделиться файлами

### Через Telegram:
Отправьте файлы себе в "Избранное"

### Через email:
```bash
# Если настроена почта
cat coffee_bot.py | mail -s "Coffee Bot" your@email.com
```

### Через облако:
Скопируйте в Dropbox, Google Drive, или Яндекс.Диск

---

## ✨ Советы

1. **Всегда делайте бэкап** перед редактированием
2. **Используйте git** для версионирования
3. **Комментируйте код** при изменениях
4. **Тестируйте** после каждого изменения

---

**Теперь вы знаете все способы открыть и посмотреть файлы бота!** 🎉
