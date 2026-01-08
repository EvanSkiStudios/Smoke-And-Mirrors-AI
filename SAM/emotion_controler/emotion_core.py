from emotion_controler.EmotionVector import EmotionVector
from emotion_controler.Emotions import BASE_EMOTIONS

if __name__ == "__main__":
    EMOTION_VECTOR = EmotionVector(BASE_EMOTIONS)

    EMOTION_VECTOR.set_emotion("Happiness", 0.3)

    print(EMOTION_VECTOR.get_emotion("Happiness"))
    print(EMOTION_VECTOR.get_strong_emotions())
