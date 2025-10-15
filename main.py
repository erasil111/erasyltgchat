import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import BOT_TOKEN, WEBHOOK_URL, ADMIN_USERNAMES, PAYPAL_LINK
from db import init_db, add_user, get_balance, consume_token, add_tokens_by_id, find_user_by_username

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

active_generations = {}


# ---------- Handlers ----------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    add_user(user.id, user.username)
    balance = get_balance(user.id)
    text = (
        f"👋 Добро пожаловать! {user.first_name or 'друг'}!\n\n"
        f"💰 Баланс: {balance} токен(ов)\n\n"
        f"Сделайте первое пробное видео всего за 300тг\n\n"
        f"✨ Команды:\n"
        f"/help — справка\n"
        f"/balance — баланс\n"
        f"/buy — купить токены\n"
        f"/generate <описание> — создать видео\n"
        f"ℹ️Используя бота, вы соглашаетесь с правилами /terms"
    )
    await message.answer(text)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "📚 Справка по использованию Sora-2 Bot\n"
"🎬 ГЕНЕРАЦИЯ ВИДЕО ИЗ ТЕКСТА\n"
"Команда: /generate <описание>\n"
"Примеры:\n"
"• /generate Кот играет на пианино в джазовом клубе\n"
"• /generate Закат над океаном, киношот\n"
"• /generate Полёт над неоновым городом\n"
"💡 Советы для качественного видео:\n"
"• Указывайте тип кадра (широкий план, крупный план)\n"
"• Опишите действие и окружение\n"
"• Добавьте свет (например, солнечный день, утреннее освещение)\n"
"Пример хорошего промпта:\n"
"Широкий план ребёнка, запускающего красный воздушный змей в парке, солнечный свет, камера плавно поднимается\n"
"🖼️ ГЕНЕРАЦИЯ ВИДЕО ИЗ ИЗОБРАЖЕНИЯ\n"
"Отправьте боту фото с подписью\n"
"В подписи укажите, что должно происходить в видео\n"
"Бот создаст видео, используя фото как первый кадр\n"
"Примеры:\n"
"• Фото комнаты: Камера медленно обходит комнату\n"
"• Фото пейзажа: Начинается дождь, дует ветер\n"
"⚠️ Важно: Фото должно соответствовать выбранному разрешению видео\n"
"⚙️ ПАРАМЕТРЫ ВИДЕО\n"
"Длительность: 4–12 секунд\n"
"Ориентация:\n"
"• 📱 Вертикальная (720x1280) — для Stories, Reels\n"
"Модели:\n"
"• 🚀 Sora-2: быстрая генерация, хорошее качество\n"
"\n"
"💰 ЦЕНЫ\n"
"Sora-2 (10 сек): 700₸\n"
"1 токен = 700₸\n"
"📦 ПАКЕТЫ ТОКЕНОВ /buy\n"
"• 700₸ — 1 видео\n"
"• 1,200₸ — 2 видео \n"
"• 2,500₸ — 5 видео \n"
"• 4,400₸ — 10 видео \n"
"Оплата: картой (PayPal) или Kaspi\n"
"📊 ДРУГИЕ КОМАНДЫ\n"
"/balance — баланс и история\n"
"/start — главное меню\n"
"❓ Частые вопросы\n"
"Q: Сколько времени занимает генерация?\n"
"A: От 2 до 10 минут, зависит от модели и длины видео\n"
"Q: Что если видео не создалось?\n"
"A: Токены автоматически возвращаются на баланс\n"
"Q: Можно ли генерировать реальных людей?\n"
"A: Нет, сервис блокирует генерацию настоящих людей\n"
"Q: Поддерживается ли русский язык?\n"
"A: Можно писать по-русски, но английский промпт точнее\n"
"💬 По вопросам: @erasyllk\n"
)
    await message.answer(text)

@dp.message(Command("terms"))
async def cmd_help(message: types.Message):
    text = (
        "ℹ️ О проекте\n"

"⚠️ Бот использует внешние сервисы для генерации видео.\n"
"Этот бот использует нейросеть Sora-2 для генерации видео по вашим описаниям.  \n"
"⚠️ Важно: вы несёте полную ответственность за тексты и контент, который создаёте с помощью бота.\n"

"❌ Запрещено использовать бота для создания:\n"
"— оскорбительного, дискриминационного или провокационного контента  \n"
"— материалов сексуального или насильственного характера  \n"
"— контента, нарушающего законы или права третьих лиц\n"

"Бот и его автор не несут ответственности за сгенерированные материалы и их дальнейшее использование.\n"

    )
    await message.answer(text)


@dp.message(Command("balance"))
async def cmd_balance(message: types.Message):
    user = message.from_user
    bal = get_balance(user.id)
    await message.answer(f"💰 Твой баланс: {bal} токен(ов)")

@dp.message(Command("invite"))
async def cmd_invite(message: types.Message):
    text = (
        "ℹ️ О проекте\n"

"Пригласи своего друга\n"
"Если он скажет что пришел от вас(ваш user name) то подарим вам 50% скидку на следующее использование\n"
    )
    await message.answer(text)


@dp.message(Command("buy"))
async def cmd_buy(message: types.Message):
    text = (
        "🟣 Оплата через PayPal или вручную\n\n"
        "📦 Пакеты:\n"
        "• 1 видео — 700₸\n"
        "• 2 видео — 1 200₸\n"
        "• 5 видео — 2 500₸\n"
        "• 10 видео — 4 400₸\n\n"
        "💰 Для ручной оплаты:\n"
        "1️⃣ Напиши администратору @erasyllk\n"
        "2️⃣ Укажи сумму и свой username\n"
        "3️⃣ Оплати(отправь чек) и жди подтверждения (5–10 мин)"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплата через PayPal", url=PAYPAL_LINK or "https://t.me/erasyllk")],
        [InlineKeyboardButton(text="🏦 Kaspi / Halyk / Freedom", url="https://t.me/erasyllk")]
    ])

    await message.answer(text, reply_markup=keyboard)


# Админ: /addtokens <username_or_id> <amount>
@dp.message(Command("addtokens"))
async def cmd_addtokens(message: types.Message):
    user = message.from_user
    admin_usernames = [x.strip().lstrip("@") for x in (ADMIN_USERNAMES or "").split(",") if x.strip()]
    if (user.username or "").lstrip("@") not in admin_usernames:
        await message.answer("❌ Доступно только администратору.")
        return

    args = message.text.split()
    if len(args) < 3:
        await message.answer("Использование: /addtokens <username или user_id> <кол-во>")
        return

    target = args[1]
    try:
        amount = int(args[2])
    except ValueError:
        await message.answer("Неверное количество. Укажи число.")
        return

    if target.startswith("@"):
        target = target.lstrip("@")

    target_id = None
    if target.isdigit():
        target_id = int(target)
    else:
        found = find_user_by_username(target)
        if found:
            target_id = found

    if not target_id:
        await message.answer("Пользователь не найден в базе. Он должен был хотя бы раз написать /start.")
        return

    add_tokens_by_id(target_id, amount)
    await message.answer(f"✅ Добавлено {amount} токен(ов) пользователю {target} (id: {target_id}).")
    try:
        await bot.send_message(target_id, f"💳 Администратор начислил вам {amount} токен(ов).")
    except Exception as e:
        logger.exception("Не удалось уведомить пользователя об начислении токенов: %s", e)


# ---------- Админ: /resetchat <username_or_id> ----------
@dp.message(Command("resetchat"))
async def cmd_resetchat(message: types.Message):
    user = message.from_user
    admin_usernames = [x.strip().lstrip("@") for x in (ADMIN_USERNAMES or "").split(",") if x.strip()]
    if (user.username or "").lstrip("@") not in admin_usernames:
        await message.answer("❌ Доступно только администратору.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /resetchat <username или user_id>")
        return

    target = args[1]
    target_id = None

    # Если передан числовой user_id
    if target.isdigit():
        target_id = int(target)
    else:
        # Ищем по username в базе
        found = find_user_by_username(target.lstrip("@"))
        if found:
            target_id = found

    if not target_id:
        await message.answer("Пользователь не найден в базе.")
        return

    # Снимаем блокировку
    if active_generations.get(target_id):
        active_generations.pop(target_id, None)
        await message.answer(f"✅ Генерация для пользователя {target} ({target_id}) сброшена. Теперь он может создавать видео.")
        try:
            await bot.send_message(target_id, "⚠️ Твоя предыдущая генерация сброшена администратором. Теперь можно создавать новое видео.")
        except Exception:
            pass
    else:
        await message.answer(f"ℹ️ Пользователь {target} ({target_id}) не был заблокирован для генерации.")



@dp.message(Command("generate"))
async def cmd_generate(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, не идёт ли уже генерация
    if active_generations.get(user_id):
        await message.answer("⚙️ Предыдущее видео ещё создаётся. Подожди немного 🙌")
        return

    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2 or not args[1].strip():
            await message.answer("⚠️ Использование: /generate <описание>")
            return

        description = args[1].strip()

        ok = consume_token(user_id)
        if not ok:
            await message.answer("💸 У тебя 0 токенов. Купи токены — /buy")
            return

        # Ставим флаг **только после всех проверок**
        active_generations[user_id] = True

        await message.answer("✅ Токен списан. Видео создаётся, это может занять 5–10 минут...")
        asyncio.create_task(_background_generate(user_id, message.chat.id, description, message.from_user.username or ""))

    except Exception as e:
        logger.exception("Ошибка в cmd_generate: %s", e)
        await message.answer("❌ Произошла ошибка. Попробуй позже.")
        add_tokens_by_id(user_id, 1)


    # флаг снимется внутри фоновой функции


# ---------- Генерация по фото ----------
@dp.message(lambda m: m.photo)
async def handle_photo(message: types.Message):
    user_id = message.from_user.id

    if active_generations.get(user_id):
        await message.answer("⚙️ Предыдущее видео ещё создаётся. Подожди немного 🙌")
        return

    try:
        caption = message.caption or ""
        photo = message.photo[-1]
        file_id = photo.file_id

        if not caption.strip():
            await message.answer("⚠️ Добавь описание к фото, чтобы я понял, что нужно сгенерировать.")
            return

        ok = consume_token(user_id)
        if not ok:
            await message.answer("💸 У тебя 0 токенов. Купи токены — /buy")
            return

        # Ставим флаг только после всех проверок
        active_generations[user_id] = True

        await message.answer("✅ Токен списан. Видео создаётся, это может занять 5–10 минут...")
        asyncio.create_task(_background_generate_photo(user_id, message.chat.id, caption, file_id, message.from_user.username or ""))

    except Exception as e:
        logger.exception("Ошибка в handle_photo: %s", e)
        await message.answer("❌ Произошла ошибка. Попробуй позже.")
        add_tokens_by_id(user_id, 1)



# ---------- background workers ----------
async def _background_generate(user_id: int, chat_id: int, prompt: str, username: str):
    """
    Работает с n8n: ждёт генерацию, обрабатывает ошибки и таймауты.
    ⚙️ Токен возвращается только при реальной ошибке.
    """
    try:
        timeout = aiohttp.ClientTimeout(total=25 * 60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            payload = {"prompt": prompt, "user_id": user_id, "username": username}
            logger.info(f"➡️ Отправляем payload в n8n: {payload}")

            async with session.post(WEBHOOK_URL, json=payload) as resp:
                text = await resp.text()
                logger.info(f"n8n ответил status={resp.status}")

                # --- Обработка ответов ---
                if resp.status == 524:
                    logger.warning("⚠️ Cloudflare timeout 524 — видео ещё генерируется.")
                    await bot.send_message(chat_id, "🕐 Видео ещё создаётся, я пришлю ссылку позже.")
                    # токен считаем потраченным
                    return

                if resp.status >= 500:
                    logger.error(f"n8n вернул 500: {text[:200]}")
                    await bot.send_message(chat_id, "❌ Ошибка сервера. Попробуй позже.")
                    add_tokens_by_id(user_id, 1)
                    return

                if resp.status >= 400:
                    logger.error(f"Ошибка клиента {resp.status}: {text[:200]}")
                    await bot.send_message(chat_id, "❌ Ошибка запроса. Попробуй изменить описание.")
                    add_tokens_by_id(user_id, 1)
                    return

                try:
                    data = await resp.json()
                except Exception:
                    logger.warning("Ответ n8n не JSON — видео, возможно, ещё в процессе.")
                    await bot.send_message(chat_id, "🕐 Видео создаётся, пришлю, когда будет готово.")
                    return  # токен не возвращаем

# --- Проверка на пустой или некорректный JSON ---
                if not data:
                    logger.warning("Ответ n8n пустой или некорректный JSON")
                    await bot.send_message(chat_id, "❌ Видео не удалось создать: некорректный ответ модели.\n💰 Токен возвращён.")
                    add_tokens_by_id(user_id, 1)
                    return

                fail_msg = data.get("failMsg") or data.get("error") or ""
                fail_code = data.get("failCode") or ""
                video_url = data.get("video_url") or data.get("videoUrl")
                state = (data.get("state") or data.get("status") or "").lower()

                # --- Специальная проверка для откровенного контента ---
                if "suggestive" in fail_msg.lower() or "racy" in fail_msg.lower() or "not allowed" in fail_msg.lower():
                    await bot.send_message(chat_id, "🚫 Нельзя генерировать откровенный контент или реальные лица.\n💰 Токен возвращён.")
                    add_tokens_by_id(user_id, 1)
                    return

        # --- Проверяем результат ---
        state = (data.get("state") or data.get("status") or "").lower()
        fail_msg = data.get("failMsg") or data.get("error") or ""
        video_url = data.get("video_url") or data.get("videoUrl")

        if state in ("fail", "failed", "error") or "cancel" in fail_msg.lower():
            logger.error(f"Ошибка модели: {fail_msg}")
            add_tokens_by_id(user_id, 1)
            await bot.send_message(
                chat_id,
                f"❌ Видео не удалось создать: {fail_msg or 'ошибка модели'}.\n💰 Токен возвращён."
            )
            return

        if not video_url:
            logger.info("Видео пока не готово (нет video_url).")
            await bot.send_message(chat_id, "🕐 Видео создаётся, я пришлю ссылку позже.")
            # токен остаётся списанным
            return

        # --- Всё ок ---
        try:
            await bot.send_video(chat_id, video=video_url, caption="🎬 Ваше видео готово!")
        except Exception as e:
            logger.warning(f"Ошибка при отправке видео: {e}")
            await bot.send_message(chat_id, f"🎬 Ваше видео готово! Ссылка: {video_url}")

    except Exception as exc:
        logger.exception(f"Непредвиденная ошибка: {exc}")
        await bot.send_message(chat_id, "⚠️ Ошибка соединения. Видео всё ещё может создаваться.")
        # токен остаётся списанным, не возвращаем

    finally:
        active_generations.pop(user_id, None)


async def _background_generate_photo(user_id: int, chat_id: int, prompt: str, file_id: str, username: str):
    """
    Работает с n8n: ждёт генерацию видео по фото.
    ⚙️ Токен возвращается только при реальной ошибке.
    """
    if not WEBHOOK_URL:
        logger.error("WEBHOOK_URL не задан в config.py/.env")
        await bot.send_message(chat_id, "❌ Внутренняя ошибка: WEBHOOK_URL не настроен. Сообщите администратору.")
        add_tokens_by_id(user_id, 1)
        return

    try:
        timeout = aiohttp.ClientTimeout(total=25 * 60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # --- Получаем прямую ссылку на фото ---
            file_url = None
            try:
                file_obj = await bot.get_file(file_id)
                file_path = file_obj.file_path
                file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                logger.info(f"Получили file_path={file_path} -> file_url={file_url}")
            except Exception as e:
                logger.exception("Не удалось получить file_path через bot.get_file: %s", e)

            # --- Отправляем запрос в n8n ---
            payload = {
                "photo_file_id": file_id,
                "photo_url": file_url,
                "prompt": prompt,
                "user_id": user_id,
                "username": username
            }
            logger.info(f"➡️ Отправляем фото-payload в n8n: {payload}")

            async with session.post(WEBHOOK_URL, json=payload) as resp:
                resp_text = await resp.text()
                logger.info(f"n8n PHOTO RESP status={resp.status}")

                # --- Обработка статусов ---
                if resp.status == 524:
                    logger.warning("⚠️ Cloudflare timeout 524 — видео ещё генерируется.")
                    await bot.send_message(chat_id, "🕐 Видео ещё создаётся, я пришлю ссылку, когда будет готово.")
                    return  # токен считаем потраченным

                if resp.status >= 500:
                    logger.error(f"n8n вернул 500: {resp_text[:200]}")
                    await bot.send_message(chat_id, "❌ Ошибка сервера. Попробуй позже.")
                    add_tokens_by_id(user_id, 1)
                    return

                if resp.status >= 400:
                    logger.error(f"Ошибка клиента {resp.status}: {resp_text[:200]}")
                    await bot.send_message(chat_id, "❌ Ошибка при генерации. Попробуй изменить описание.")
                    add_tokens_by_id(user_id, 1)
                    return

                # --- Парсим JSON ---
                try:
                    data = await resp.json()
                except Exception:
                    logger.warning("Ответ n8n не JSON — возможно, видео ещё генерируется.")
                    await bot.send_message(chat_id, "🕐 Видео создаётся, пришлю позже.")
                    return  # токен не возвращаем

        # --- Проверяем ответ ---

        if not data:
            logger.warning("Ответ n8n пустой или некорректный JSON")
            await bot.send_message(chat_id, "❌ Видео не удалось создать: некорректный ответ модели.\n💰 Токен возвращён.")
            add_tokens_by_id(user_id, 1)
            return
        
        state = (data.get("state") or data.get("status") or "").lower()
        fail_msg = data.get("failMsg") or data.get("error") or ""
        video_url = data.get("video_url") or data.get("videoUrl")

        if "suggestive" in fail_msg.lower() or "racy" in fail_msg.lower() or "not allowed" in fail_msg.lower():
           await bot.send_message(chat_id, "🚫 Нельзя генерировать фото реальных людей или откровенный контент.\n💰 Токен возвращён.")
           add_tokens_by_id(user_id, 1)
           return


        if state in ("fail", "failed", "error") or "cancel" in fail_msg.lower():
            logger.error(f"Ошибка модели: {fail_msg}")
            add_tokens_by_id(user_id, 1)
            await bot.send_message(
                chat_id,
                f"❌ Видео не удалось создать: {fail_msg or 'ошибка модели'}.\n💰 Токен возвращён."
            )
            return

        if not video_url:
            logger.info("Видео пока не готово (нет video_url).")
            await bot.send_message(chat_id, "🕐 Видео создаётся, пришлю ссылку, когда будет готово.")
            return  # токен не возвращаем

        # --- Успешно: отправляем видео ---
        try:
            await bot.send_video(chat_id, video=video_url, caption="🎬 Ваше видео готово!")
        except Exception as e:
            logger.warning(f"Ошибка при отправке видео: {e}")
            await bot.send_message(chat_id, f"🎬 Ваше видео готово! Ссылка: {video_url}")

    except Exception as exc:
        logger.exception(f"Ошибка при генерации видео из фото: {exc}")
        try:
            await bot.send_message(chat_id, "⚠️ Ошибка соединения. Видео всё ещё может создаваться.")
        except Exception:
            pass
        # токен не возвращаем — т.к. видео может быть в процессе

    finally:
        # Снимаем флаг активности, чтобы можно было снова генерировать
        active_generations.pop(user_id, None)




# ---------- startup ----------
async def main():
    init_db()
    logger.info("Бот запущен")
    logger.info("WEBHOOK_URL = %s", WEBHOOK_URL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
