class Emotion:
    def __init__(self, name):
        self.name = name.capitalize()
        self.value = 0


# List of possible Base Emotions
BASE_EMOTIONS = (
    "Anger",
    "Disgust",
    "Fear",
    "Happiness",
    "Sadness",
    "Surprise",
)