import en_core_web_sm

nlp = en_core_web_sm.load()

WEATHER_KEYWORDS = {
    "weather", "temperature", "forecast",
    "rain", "snow", "sunny", "cloudy", "storm",
    "hot", "cold", "warm", "chilly"
}

REQUEST_VERBS = {
    "tell", "check", "give", "show", "get", "forecast", "look"
}

INTERROGATIVE_WORDS = {"what", "whats", "how", "is", "are", "will", "can", "should"}

def _has_weather_intent(doc) -> bool:
    # Explicit question mark
    if doc.text.strip().endswith("?"):
        return True

    for sent in doc.sents:
        # 1. Interrogative auxiliary attached to root
        for token in sent:
            if token.dep_ == "aux" and token.lemma_ in {"be", "do", "will", "can", "should"}:
                return True

        # 2. Sentence contains an interrogative word
        if any(token.lemma_.lower() in INTERROGATIVE_WORDS for token in sent):
            return True

        # 3. Imperative root verb
        if sent.root.pos_ == "VERB" and sent.root.lemma_ in REQUEST_VERBS:
            return True

    return False




def _has_location(doc) -> tuple[bool, list[str]]:
    """
    Returns True and a list of location entities if any GPE or LOC exists.
    """
    locations = [ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC"}]
    return bool(locations), locations


def _has_weather_topic(doc) -> tuple[bool, list[str]]:
    """
    Returns True and a list of weather keywords found in the text.
    """
    topics = [token.text for token in doc if token.lemma_.lower() in WEATHER_KEYWORDS]
    return bool(topics), topics


def is_weather_request(text: str, debug=False) -> bool:
    """
    Returns True if the text is a weather request: requires location, weather topic, and intent.
    Debug prints explain why a sentence passes or fails.
    """
    if not text or not text.strip():
        if debug:
            print("Empty text → False")
        return False

    doc = nlp(text)

    # 1️⃣ Must have location
    has_loc, locs = _has_location(doc)
    if not has_loc:
        if debug:
            print(f"No location found. Entities: {[(ent.text, ent.label_) for ent in doc.ents]}")
        return False
    if debug:
        print(f"Location found: {locs}")

    # 2️⃣ Must have weather topic
    has_topic, topics = _has_weather_topic(doc)
    if not has_topic:
        if debug:
            print(f"No weather topic found. Tokens matching keywords: {topics}")
        return False
    if debug:
        print(f"Weather topic found: {topics}")

    # 3️⃣ Must have intent
    has_intent = _has_weather_intent(doc)
    if not has_intent:
        if debug:
            for sent in doc.sents:
                print(f"No intent detected. Sentence root: {sent.root.text}, pos: {sent.root.pos_}, lemma: {sent.root.lemma_}")
        return False
    if debug:
        print("Intent detected")

    return True
