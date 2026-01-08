from emotion_controler.EmotionVector import EmotionVector
from emotion_controler.Emotions import BASE_EMOTIONS

if __name__ == "__main__":
    EMOTION_VECTOR = EmotionVector(BASE_EMOTIONS)
    print(EMOTION_VECTOR.get_strong_emotions())
