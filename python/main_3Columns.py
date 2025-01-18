import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import config as cnf
import voice

bot = telebot.TeleBot(cnf.bot_token)

# Состояние выбора голоса и ожидания текста
user_state = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Получаем доступные голоса
    voices = voice.get_available_voices()
    voices = [str(voice['name']) for voice in voices]
    
    # Создаем клавиатуру с голосами
    keyboard = create_keyboard(voices, columns=3)
    
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для озвучивания текста! Выберите голос, которым будет озвучен ваш текст.",
        reply_markup=keyboard
    )
    user_state[message.chat.id] = {"state": "choosing_voice"}

@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("state") == "choosing_voice")
def choose_voice(message):
    chosen_voice = message.text
    available_voices = voice.get_available_voices()
    available_voices = [str(voice['name']) for voice in available_voices]
    
    if chosen_voice not in available_voices:
        bot.send_message(message.chat.id, "Пожалуйста, выберите голос из предложенных.")
        return
    
    user_state[message.chat.id] = {"state": "waiting_for_text", "voice": chosen_voice}
    bot.send_message(message.chat.id, f"Вы выбрали голос: {chosen_voice}. Теперь введите текст, который вы хотите озвучить.")

@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get("state") == "waiting_for_text")
def generate_audio_message(message):
    user_info = user_state.get(message.chat.id)
    if not user_info:
        bot.send_message(message.chat.id, "Что-то пошло не так. Попробуйте начать с команды /start.")
        return
    
    chosen_voice = user_info["voice"]
    text = message.text
    
    try:
        # Генерация аудио
        audio_file = voice.generate_audio(text, chosen_voice)
        
        # Отправка аудиофайла
        with open(audio_file, 'rb') as audio:
            bot.send_audio(message.chat.id, audio)
        
        # Отправка голосового сообщения
        with open(audio_file, 'rb') as audio:
            bot.send_voice(message.chat.id, audio)
        
        bot.send_message(message.chat.id, "Готово! Если хотите озвучить еще текст, выберите новый голос или начните заново с /start.")
        user_state.pop(message.chat.id, None)  # Сброс состояния

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

def create_keyboard(voices, columns=2):
    """
    Создает клавиатуру с кнопками голосов, распределяя их по заданному количеству колонок.
    
    :param voices: Список голосов (имен).
    :param columns: Количество колонок.
    :return: Клавиатура с кнопками.
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for index, voice_name in enumerate(voices):
        row.append(KeyboardButton(voice_name))
        if (index + 1) % columns == 0:  # Если достигли лимита колонок
            keyboard.add(*row)  # Добавляем строку в клавиатуру
            row = []  # Очищаем текущую строку
    if row:  # Добавляем оставшиеся кнопки, если они есть
        keyboard.add(*row)
    return keyboard

# Запуск бота
print("Бот запущен")
bot.polling()