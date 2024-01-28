from elevenlabs import voices, generate


voices = voices()
for voice in voices:
    print(voice)