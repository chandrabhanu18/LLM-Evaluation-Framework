from typing import Callable

_CUSTOM_REGISTRY = {}


def register_metric(name: str, constructor: Callable):
    _CUSTOM_REGISTRY[name] = constructor


def get_custom(name: str):
    return _CUSTOM_REGISTRY.get(name)
