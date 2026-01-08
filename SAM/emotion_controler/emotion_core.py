from emotion_controler.EmotionVector import EmotionVector
from emotion_controler.Emotions import BASE_EMOTIONS

if __name__ == "__main__":
    EMOTION_VECTOR = EmotionVector(BASE_EMOTIONS)

    print(EMOTION_VECTOR.get_emotion("anger"))
    EMOTION_VECTOR.set_emotion("happiness", 0.3)

    print(EMOTION_VECTOR.get_emotion("happiness"))
    print(EMOTION_VECTOR.get_strong_emotions())
    print(EMOTION_VECTOR.get_emotion("anger"))
