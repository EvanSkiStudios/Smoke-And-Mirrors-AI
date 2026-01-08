from emotion_controler.Emotions import Emotion

EPSILON = 1e-6  # Small threshold for floating-point comparisons
# 0.000001


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
        if total < EPSILON:
            # Avoid division by zero, distribute evenly
            n = len(self.emotions)
            for emotion in self.emotions.values():
                emotion.value = 1 / n
        else:
            for emotion in self.emotions.values():
                emotion.value /= total

    def add_delta(self, deltas: dict):
        """Add changes to emotions and normalize."""
        for name, delta in deltas.items():
            name = name.capitalize()
            if name in self.emotions:
                self.emotions[name].value += delta
                if self.emotions[name].value < EPSILON:
                    self.emotions[name].value = 0.0
        self.normalize()

    def get_dominant(self):
        """Return the emotion(s) with the highest value, accounting for epsilon"""
        max_value = max(e.value for e in self.emotions.values())
        dominant = [e.name for e in self.emotions.values() if abs(e.value - max_value) < EPSILON]
        return dominant, max_value

    def get_strong_emotions(self):
        """
        Returns emotions that are significantly stronger than a calm (uniform) state.
        """
        n = len(self.emotions)
        baseline = 1 / n
        return [
            e.name
            for e in self.emotions.values()
            if e.value - baseline > EPSILON
        ]

    def set_emotion(self, name: str, value: float) -> None:
        """Set a specific emotion while keeping proportions of the others, sum stays 1."""
        name = name.capitalize()
        if name not in self.emotions:
            return

        value = max(0.0, float(value))
        remaining_total = 1.0 - value

        # Sum of all other emotions
        other_sum = sum(e.value for e_name, e in self.emotions.items() if e_name != name)

        if other_sum < EPSILON:
            # If all others are effectively zero, distribute remaining_total evenly
            n = len(self.emotions) - 1
            for e_name, e in self.emotions.items():
                if e_name != name:
                    e.value = remaining_total / n if n > 0 else 0.0
        else:
            # Scale others proportionally
            scale = remaining_total / other_sum
            for e_name, e in self.emotions.items():
                if e_name != name:
                    e.value *= scale

        # Set the target emotion
        self.emotions[name].value = value

    def get_emotion(self, name: str) -> float:
        """Returns the current value of the emotion"""
        name = name.capitalize()
        if name in self.emotions:
            return self.emotions[name].value
        return -1
