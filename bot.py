import string
import re
import hashlib
import logging
import requests
import secrets
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# Получаем токен из .env файла
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Место для хранения ID сообщений, которые мы отправляем
user_messages = {}

# Список популярных паролей (исходя из открытых данных)
COMMON_PASSWORDS = {
    "123456", "password", "123456789", "12345", "12345678", "qwerty", "abc123", "111111", "123123", "password1",
    "1234", "qwerty123", "1q2w3e4r", "123qwe", "letmein", "monkey", "dragon", "sunshine", "123321", "qwertyuiop"
}


# Проверка "похожих" паролей
def is_password_common(password: str) -> bool:
    simplified = re.sub(r'[^a-zA-Z0-9]', '', password.lower())  # Убираем спецсимволы
    return simplified in COMMON_PASSWORDS


# Проверка, был ли пароль скомпрометирован через Have I Been Pwned
def check_password_breach(password: str) -> bool:
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]

    try:
        response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
        response.raise_for_status()
        if suffix in response.text:
            return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при проверке пароля: {e}")
    return False


# Оценка времени взлома пароля
def estimate_crack_time(password: str) -> tuple:
    if is_password_common(password):
        return 0.001, "секунд"  # Практически мгновенный взлом

    attempts_per_second = 1_000_000_000  # 1 миллиард попыток в секунду

    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digits = any(c.isdigit() for c in password)
    has_special = any(c in string.punctuation for c in password)

    charset_size = 0
    if has_lower:
        charset_size += 26  # количество букв в нижнем регистре
    if has_upper:
        charset_size += 26  # количество букв в верхнем регистре
    if has_digits:
        charset_size += 10  # количество цифр
    if has_special:
        charset_size += len(string.punctuation)  # количество спецсимволов

    if len(password) < 8:
        return 0.1, "секунд"  # Пароль слишком короткий, сразу легко взломать

    total_combinations = charset_size ** len(password)
    estimated_time = total_combinations / attempts_per_second  # Время в секундах

    # Если время слишком большое, выводим в годах, месяцах или днях
    if estimated_time >= 31_536_000:  # Время больше года (31,536,000 секунд в году)
        estimated_time_in_years = estimated_time / 31_536_000  # Переводим в годы
        return estimated_time_in_years, "лет"
    elif estimated_time >= 2_592_000:  # Время больше месяца (2,592,000 секунд в месяце)
        estimated_time_in_months = estimated_time / 2_592_000  # Переводим в месяцы
        return estimated_time_in_months, "месяцев"
    elif estimated_time >= 86_400:  # Время больше дня (86,400 секунд в сутках)
        estimated_time_in_days = estimated_time / 86_400  # Переводим в дни
        return estimated_time_in_days, "дней"

    return estimated_time, "секунд"  # Время в секундах


# Рекомендации по улучшению пароля
def generate_recommendation(time_to_crack: float, time_unit: str, password: str) -> str:
    recommendations = []
    if is_password_common(password):
        return "⚠ Ваш пароль слишком распространён! Измените его."

    if check_password_breach(password):
        return "🚨 Ваш пароль был скомпрометирован в утечке! Измените его."

    if len(password) < 8:
        recommendations.append("Добавьте больше символов (минимум 8-12).")

    if not any(c.isdigit() for c in password):
        recommendations.append("Добавьте хотя бы одну цифру.")

    if not any(c in string.punctuation for c in password):
        recommendations.append("Добавьте хотя бы один спецсимвол.")

    if not any(c.isupper() for c in password):
        recommendations.append("Добавьте заглавные буквы.")

    if time_to_crack < 1:
        recommendations.append("Пароль можно взломать мгновенно, сделайте его сложнее!")

    if recommendations:
        return "⚠ Ваш пароль можно улучшить:\n- " + "\n- ".join(recommendations)
    else:
        # Форматируем время взлома
        return f"✅ Отличный пароль! Он может быть подобран за {time_to_crack:.2f} {time_unit}."


# Подсказка по созданию пароля
def password_tip():
    return (
        "💡 **Как создать хороший пароль?**\n"
        "1. Используйте минимум 12 символов.\n"
        "2. Включайте заглавные и строчные буквы.\n"
        "3. Добавьте цифры и спецсимволы.\n"
        "4. Избегайте использования личной информации.\n"
        "5. Используйте случайные комбинации."
    )


# Генерация надежного пароля
def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


# Команды для настройки пароля
async def send_settings(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton('Минимальная длина')
    button2 = KeyboardButton('Минимальные символы')
    button3 = KeyboardButton('Подсказка по созданию пароля')
    button4 = KeyboardButton('Сгенерируй мне пароль')
    markup.add(button1, button2, button3, button4)
    await message.answer("Выберите параметр для настройки пароля:", reply_markup=markup)


# Обработка команды /start с моментальной отправкой кнопок
@dp.message_handler(commands=['start'])
async def start_command(message: Message):
    logger.info(f"User {message.from_user.id} started the bot.")
    await message.answer("👋 Привет! Введите пароль для проверки его надежности:")
    await send_settings(message)  # Показываем кнопки сразу после приветствия


# Обработка команды /settings
@dp.message_handler(commands=['settings'])
async def settings_command(message: Message):
    await send_settings(message)


# Обработка нажатия кнопок
@dp.message_handler(lambda message: message.text == 'Подсказка по созданию пароля')
async def tip_password(message: Message):
    await message.answer(password_tip())


@dp.message_handler(lambda message: message.text == 'Минимальная длина')
async def min_length(message: Message):
    await message.answer("Минимальная длина пароля должна быть 8 символов. Рекомендуется использовать 12 и более.")


@dp.message_handler(lambda message: message.text == 'Минимальные символы')
async def min_symbols(message: Message):
    await message.answer("Пароль должен содержать как минимум одну цифру и один спецсимвол (например, !, @, #).")


@dp.message_handler(lambda message: message.text == 'Сгенерируй мне пароль')
async def generate_password(message: Message):
    new_password = generate_random_password()
    await message.answer(
        f"🛠 Сгенерированный пароль: {new_password}\n(Вы можете использовать этот пароль для регистрации.)")


@dp.message_handler()
async def check_password(message: Message):
    password = message.text
    estimated_time, time_unit = estimate_crack_time(password)
    recommendation = generate_recommendation(estimated_time, time_unit, password)

    # Отправляем сообщение о пароле
    sent_message = await message.answer(
        f"⏳ Ваш пароль можно подобрать за: {estimated_time:.2f} {time_unit}\n{recommendation}")

    # Сохраняем ID отправленного сообщения
    if message.from_user.id not in user_messages:
        user_messages[message.from_user.id] = []

    user_messages[message.from_user.id].append(sent_message.message_id)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
