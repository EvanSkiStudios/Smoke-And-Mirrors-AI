from types import SimpleNamespace


def namespace(d: dict) -> SimpleNamespace:
    return SimpleNamespace(**{
        k: namespace(v) if isinstance(v, dict) else v for k, v in d.items()
    })
