# Telegram Business Bot

Бот для автоматического перевода подарков в Telegram Business API.

## 🚀 Деплой на Railway

### Пошаговая инструкция:

#### 1. Создание GitHub репозитория
1. Зайдите на [github.com](https://github.com)
2. Нажмите "New repository" (зеленая кнопка)
3. Назовите репозиторий: `telegram-business-bot`
4. Оставьте его публичным
5. Нажмите "Create repository"

#### 2. Загрузка файлов в GitHub
1. Скачайте все файлы из этой папки
2. В созданном репозитории нажмите "uploading an existing file"
3. Перетащите все файлы:
   - `lox.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `.gitignore`
   - `README.md`
4. Нажмите "Commit changes"

#### 3. Регистрация на Railway
1. Зайдите на [railway.app](https://railway.app)
2. Нажмите "Login with GitHub"
3. Разрешите доступ к вашему GitHub аккаунту

#### 4. Создание проекта на Railway
1. Нажмите "New Project"
2. Выберите "Deploy from GitHub repo"
3. Найдите ваш репозиторий `telegram-business-bot`
4. Нажмите "Deploy Now"

#### 5. Настройка переменных окружения
1. В проекте Railway перейдите в раздел "Variables"
2. Добавьте переменные:
   - `BOT_TOKEN` = `7339741334:AAGKYivJ5ttvDxvC4OgAXpQs0quNQHpn0ww`
   - `ADMIN_ID` = `1948254891`
3. Нажмите "Add"

#### 6. Запуск бота
1. Railway автоматически запустит бота
2. В разделе "Deployments" вы увидите статус
3. Если статус "Deployed" - бот работает!

## 📱 Использование бота

1. Найдите бота в Telegram: `@ваш_бот_username`
2. Отправьте `/start`
3. Подключите как Business Bot в настройках Telegram
4. Бот автоматически начнет работать!

## 🔧 Команды администратора

- `/start` - информация о боте
- `/check_gifts` - проверить и перевести подарки

## 📊 Мониторинг

- Логи доступны в разделе "Deployments" на Railway
- Файлы данных сохраняются в облаке
- Бот работает 24/7 автоматически 