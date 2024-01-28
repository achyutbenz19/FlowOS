import os
import pyaudio
import wave
import audioop
import math
from pydub import AudioSegment
from gradio_client import Client
from dotenv import load_dotenv
load_dotenv()

hugging_face = Client("YouLearn/faster-whisper")

def convert_to_mp3(wav_filename, mp3_filename):
    """
    Convert a WAV file to MP3 format.

    :param wav_filename: Filename of the input WAV file.
    :param mp3_filename: Filename of the output MP3 file.
    """
    audio = AudioSegment.from_wav(wav_filename)
    audio.export(mp3_filename, format="mp3")

def record_audio(output_filename, format=pyaudio.paInt16, channels=1, rate=44100, chunk=1024, silence_threshold=62, silence_duration=1):
    """
    Record audio from the microphone until silence is detected.

    :param output_filename: Filename to save the recorded audio.
    :param format: Audio format (default is 16-bit PCM).
    :param channels: Number of audio channels (default is 1 for mono).
    :param rate: Sample rate (default is 44100 Hz).
    :param chunk: Data chunk size for processing (default is 1024).
    :param silence_threshold: Silence threshold in dB (default is 30 dB).
    :param silence_duration: Duration of silence in seconds to stop recording (default is 2 seconds).
    """
    global is_recording
    is_recording = True

    def rms(frame):
        """Calculate the root mean square of the audio frame."""
        return audioop.rms(frame, 2)

    def is_silent(rms_val):
        """Check if the given RMS value indicates silence."""
        if rms_val == 0:  # Avoid log10 of zero which will cause math domain error
            return True
        return 20 * math.log10(rms_val) < silence_threshold


    audio = pyaudio.PyAudio()
    stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

    print("Recording...")

    frames = []
    silent_chunks = 0
    silent_for_duration = False

    while is_recording:
        data = stream.read(chunk)
        rms_val = rms(data)

        if is_silent(rms_val):
            silent_chunks += 1
            if silent_chunks >= silence_duration * rate / chunk:
                print("Silence detected, stopping recording.")
                silent_for_duration = True
                break
        else:
            silent_chunks = 0

        frames.append(data)

    if not silent_for_duration:
        print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    
    output_file = "output.mp3"
    convert_to_mp3(output_filename, output_file)
    os.remove(output_filename)
    print("Transcribing...")
    output = hugging_face.predict(output_file, "tiny")
    print(f"Transcribe successfull!: {output}")
    transcript = output['transcript']
    final_transcript = ""
    for chunk in transcript:
        final_transcript += chunk['text'] + " "
    os.remove(output_file)
    return final_transcript

def stop_recording():
    global is_recording
    is_recording = False 

if __name__ == "__main__":
    audio = record_audio("output.wav")
    print(audio)