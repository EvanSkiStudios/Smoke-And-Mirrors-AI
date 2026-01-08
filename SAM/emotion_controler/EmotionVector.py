from emotion_controler.Emotions import Emotion


class EmotionVector:
    def __init__(self, base_emotions):
        # Create list of emotions and bind their name to their instance
        self.emotions = {name: Emotion(name) for name in base_emotions}
        self.normalize()

    def as_dict(self):
        return {emotion.name: emotion.value for emotion in self.emotions.values()}

    def normalize(self):
        """Sets all emotions to be evenly distributed - consider this calm"""
        total = sum(emotion.value for emotion in self.emotions.values())
        if total == 0:
            # Avoid division by zero, distribute evenly
            n = len(self.emotions)
            for emotion in self.emotions.values():
                emotion.value = 1 / n
        else:
            for emotion in self.emotions.values():
                emotion.value /= total

    def add_delta(self, deltas: dict):
        """Add changes to emotions and normalize."""
        # E.add_delta({"Happiness": 0.3, "Surprise": 0.1})
        for name, delta in deltas.items():
            if name in self.emotions:
                self.emotions[name].value += delta
                if self.emotions[name].value < 0:
                    self.emotions[name].value = 0
        self.normalize()

    def get_dominant(self):
        max_value = max(e.value for e in self.emotions.values())
        dominant = [e.name for e in self.emotions.values() if e.value == max_value]
        return dominant, max_value

    def get_strong_emotions(self):
        """
        Returns emotions that are significantly stronger than a calm (uniform) state.
        Returns:
            list[str]: Names of emotions that exceed the calm amount.
        """
        n = len(self.emotions)
        baseline = 1 / n
        return [
            e.name
            for e in self.emotions.values()
            if e.value >= baseline
        ]

    def set_emotion(self, name: str, value: float, normalize: bool = True) -> None:
        if name in self.emotions:
            self.emotions[name].value = max(0.0, float(value))
            if normalize:
                self.normalize()

    def get_emotion(self, name: str) -> float:
        """"Returns the current value of the emotion"""
        if name in self.emotions:
            return self.emotions[name].value
