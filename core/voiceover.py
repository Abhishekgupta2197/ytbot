import json
import base64
import sys
sys.path.append('/home/ubuntu/ytbot')
from config import ELEVENLABS_API_KEY
from core.credit_tracker import can_generate, track_usage

VOICE_ID = "onwK4e9ZLuTAKqWW03F9"  # Daniel — deep dramatic British narrator

def generate_voiceover(text, output_path):
    print("🎙️ Generating voiceover with ElevenLabs...")

    if not can_generate(text):
        raise Exception("ElevenLabs credits exhausted. Bot paused until reset on 21st.")

    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    response = client.text_to_speech.convert_with_timestamps(
        voice_id=VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.4,
            similarity_boost=0.75,
            style=0.6,
            use_speaker_boost=True
        )
    )

    audio_bytes = base64.b64decode(response.audio_base_64)
    with open(output_path, "wb") as f:
        f.write(audio_bytes)

    # Track usage after successful generation
    track_usage(text)

    timing_path = output_path.replace(".mp3", "_timings.json")
    word_timings = []
    alignment = response.normalized_alignment or response.alignment

    if alignment:
        chars = alignment.characters
        starts = alignment.character_start_times_seconds
        ends = alignment.character_end_times_seconds

        current_word = ""
        word_start = 0
        for i, (char, start, end) in enumerate(zip(chars, starts, ends)):
            is_last = i == len(chars) - 1
            if char == " " or is_last:
                if is_last and char != " ":
                    current_word += char
                if current_word.strip():
                    word_timings.append({
                        "word": current_word,
                        "start": word_start,
                        "duration": end - word_start
                    })
                current_word = ""
                word_start = end
            else:
                if not current_word:
                    word_start = start
                current_word += char

    with open(timing_path, "w") as f:
        json.dump(word_timings, f)

    print(f"✅ Got {len(word_timings)} exact word timestamps!")
    print("✅ Voiceover saved!")
