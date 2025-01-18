from elevenlabs import play, save
from elevenlabs.client import ElevenLabs
import config as cnf

client = ElevenLabs(
    api_key=cnf.elevenlabs_api_key,
)

def get_available_voices():
    """
    Возвращает список всех доступных голосов.
    """
    voices = client.voices.get_all()
    return [{'name': voice.name, 'id': voice.voice_id} for voice in voices.voices]

def generate_audio(text: str, voice: str):
    """
    Возвращает сгенерированное аудио с указанным голосом и текстом.

    :param voice_name: Имя голоса, который будет использоваться для генерации.
    :param text: Текст, который нужно озвучить.
    :return: Сгенерированный аудиофайл в формате bytes.
    """
    audio = client.generate(
        text=text,
        voice=voice,
        model="eleven_multilingual_v2"
    )
    name = "audio.mp3"
    save(audio, name)
    return name

#print(get_available_voices())
