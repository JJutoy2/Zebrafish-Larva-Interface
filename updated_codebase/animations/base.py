# animations/base.py
from abc import ABC, abstractmethod
import inspect

_ANIM_REGISTRY: dict = {}

def register_animation(name):
    def deco(cls):
        _ANIM_REGISTRY[name] = cls
        return cls
    return deco

def make_animation(name, **kwargs):
    print(f"Making animation '{name}' with params {kwargs}")
    if not (name in _ANIM_REGISTRY.keys()):
        raise ValueError(f"Unknown animation, make sure the animation class of '{name}' was called")
    
    cls = _ANIM_REGISTRY[name]
    sig = inspect.signature(cls.__init__)
    valid_params = set(sig.parameters.keys()) - {"self"}
    invalid_kwargs = set(kwargs.keys()) - valid_params
    if invalid_kwargs:
        raise TypeError(f"Invalid arguments for '{name}': {invalid_kwargs}. Valid arguments are: {valid_params}")
   
    return cls(**kwargs)

class Animation(ABC):
    def on_start(self, surface, **kwargs):
        """Allocate resources. Called once after construction."""
        pass

    def on_event(self, event):
        """Optional: react to keyboard/mouse/controller."""
        pass

    @abstractmethod
    def update(self, dt: float):
        """Advance simulation by dt seconds. No drawing here."""
        ...

    @abstractmethod
    def draw(self, surface):
        """Draw current state. No simulation here."""
        ...

    def on_stop(self):
        """Free resources if needed."""
        pass

