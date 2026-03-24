import asyncio
import os
import re

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from elevenlabs.core.api_error import ApiError
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

# Load Env
load_dotenv()
API_KEY = os.getenv("ELEVENLABS_API_KEY")

voices_dict = {
    "VOICES": {
        "DEFAULT": os.getenv("ELEVENLABS_VOICE_ID"),
        "SAM": os.getenv("VOICE_ID_SAM"),
        "ISABEL": os.getenv("VOICE_ID_ISABEL"),
        "GILBERT": os.getenv("VOICE_ID_GILBERT"),
        "COLT": os.getenv("VOICE_ID_COLT"),
        "HERMA": os.getenv("VOICE_ID_HERMA"),
    }
}
VOICES = voices_dict["VOICES"]

client = ElevenLabs(
    api_key=f"{API_KEY}"
)


def clean_text(text: str) -> str:
    # Remove *...* and [...] including the markers
    cleaned = re.sub(r"(\*.*?\*|\[.*?\])", "", text)
    # Remove specific symbols
    cleaned = re.sub(r"[!?\@$%^&\";:]", "", cleaned)
    # Remove extra spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Limit to at most 10 characters
    if cleaned == "":
        cleaned = 'text_to_speech'
    return cleaned[:14]


async def text_to_speech(text: str, file_name='text_to_speech', voice="default"):
    logger.info("Starting TTS Message")

    if voice is not None:
        voice_id = VOICES.get(voice.upper(), VOICES["DEFAULT"])
    else:
        voice_id = VOICES["DEFAULT"]

    def _blocking_tts():
        try:
            audio = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_v3",
                output_format="mp3_44100_128",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    use_speaker_boost=False,
                    similarity_boost=0.5,
                    style=0.5,
                    speed=1.0,
                ),
            )

            # Collect into bytes
            audio_bytes = b"".join(audio)

            # Save to file
            file_path = f"{clean_text(file_name)}.mp3"
            with open(file_path, "wb") as f:
                f.write(audio_bytes)

            logger.debug(f"✅ Audio saved as {os.path.abspath(file_path)}")
            return os.path.abspath(file_path)

        except ApiError as e:
            logger.error(
                f"API Error while generating TTS: {e}\n"
                f"Status code: {e.status_code}\n"
                f"Response body: {e.body}"
            )
            return None
        except Exception as e:
            logger.exception(f"Unexpected error during TTS: {e}")
            return None

    # Run the blocking code in a separate thread
    file_path = await asyncio.to_thread(_blocking_tts)
    return file_path
