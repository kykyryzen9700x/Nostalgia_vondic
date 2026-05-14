import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))
from botiksdk import Bot, Dispatcher, Command, F
from backend.config import config
from backend.database.models import create_ticket_from_bot, get_user_by_vondic_id

BOT_TOKEN = 'Rvwa2_GWKjQ2ifGtUFXBwu78dqKHW9k-buQrYAzi56c'
BOT_ID = 'ec77f86b-1c57-400d-a5e8-948be0a6f22f'
BASE_URL = 'https://vondic.knopusmedia.ru'
ADMIN_CHAT_ID = '5cf17a45-2907-4819-bd28-a1d28470999a'

dp = Dispatcher()
bot = Bot(bot_id=BOT_ID, token=BOT_TOKEN, base_url=BASE_URL)

@dp.message(Command("start"))
async def cmd_start(message, bot, state):
    print(f"[BOT] /start from {message.chat.id}")
    await bot.send_message(
        str(message.chat.id),
        "🤖 Бот технической поддержки.\nОтправьте ваше сообщение, и мы ответим вам как можно скорее."
    )

@dp.message(F.message.text)
async def handle_support_message(message, bot, state):
    chat_id = str(message.chat.id)
    text = message.text.strip()
    print(f"[BOT] Получено сообщение от {chat_id}: {text[:50]}")

    if not text:
        return

    # Пытаемся найти пользователя в нашей БД по vondic_user_id
    vondic_user_id = str(message.from_user.id) if message.from_user else None
    local_user_id = None
    if vondic_user_id:
        user = get_user_by_vondic_id(vondic_user_id)
        if user:
            local_user_id = user['id']

    # Создаём тикет
    ticket_id = create_ticket_from_bot(chat_id, text, local_user_id)
    print(f"[BOT] Создан тикет #{ticket_id}")

    # Уведомление администратору (опционально)
    if ADMIN_CHAT_ID:
        try:
            from botiksdk.client import PublicAPIClient
            client = PublicAPIClient(base_url=BASE_URL)
            bot_id = BOT_ID
            client.send_message(
                bot_id=bot_id,
                bot_token=BOT_TOKEN,
                chat_id=ADMIN_CHAT_ID,
                text=f"🆕 Новое обращение #{ticket_id}\nОт: {chat_id}\nСообщение: {text[:200]}"
            )
        except Exception as e:
            print(f"Ошибка уведомления админа: {e}")

    await bot.send_message(
        chat_id,
        f"✅ Ваше обращение #{ticket_id} принято. Мы ответим вам в ближайшее время."
    )

async def main():
    print("Бот поддержки запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
