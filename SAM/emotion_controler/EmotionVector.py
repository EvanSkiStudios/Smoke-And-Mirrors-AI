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

    def get_strong_emotions(self, strength_factor=2.0):
        """
        Returns emotions that are significantly stronger than a calm (uniform) state.

        The emotion vector is always normalized, so all emotion values sum to 1.
        A calm state is defined as an even distribution across all emotions,
        where each emotion has a baseline value of 1 / N.

        An emotion is considered "strong" if its value exceeds the calm baseline
        multiplied by `strength_factor`.

        This provides a non-arbitrary, scalable definition of dominance:
        - It adapts automatically to the number of emotions tracked
        - It detects emotions that stand out meaningfully from calm
        - An empty result implies the overall state is calm

        Parameters:
            strength_factor (float): How many times stronger than calm an emotion
                                      must be to be considered strong.
                                      Example: 2.0 = twice the calm baseline.

        Returns:
            list[str]: Names of emotions that exceed the dominance threshold.
        """

        n = len(self.emotions)
        baseline = 1 / n
        return [
            e.name
            for e in self.emotions.values()
            if e.value >= baseline * strength_factor
        ]

    def set_emotion(self, name: str, value: float, normalize: bool = True) -> None:
        if name in self.emotions:
            self.emotions[name].value = max(0.0, float(value))
            if normalize:
                self.normalize()
