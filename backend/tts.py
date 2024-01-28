from elevenlabs import generate, play, voices
from dotenv import load_dotenv
load_dotenv()

voices = voices()

voice_map = {
    voice.name: voice for voice in voices
}
def speak(text: str, voice: str = "Thomas"):
    voice = voice_map[voice]
    audio = generate(
    text=text,
    voice=voice
    )
    play(audio)
