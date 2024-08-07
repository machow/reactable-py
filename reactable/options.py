from __future__ import annotations

from dataclasses import dataclass, field
from .models import Theme, Language


@dataclass
class Options:
    theme: Theme = field(default_factory=Theme)
    language: Language = field(default_factory=Language)

    def __setattr__(self, name, value):
        # validate options
        if name == "theme" and not isinstance(value, Theme):
            raise TypeError(f"Expected Theme, got {type(value)}")

        super().__setattr__(name, value)

    def reset(self):
        self.theme = Theme()
        self.language = Language()


options = Options()
