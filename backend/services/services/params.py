import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParamLimits:
    """Bornes et valeurs par défaut des réglages de génération.

    Ces valeurs viendront de Settings (JAR-09) ; elles ont ici des défauts
    raisonnables pour que le module fonctionne seul.
    """
    default_temperature: float = 0.7
    min_temperature: float = 0.0
    max_temperature: float = 2.0
    default_max_tokens: int = 1024
    min_max_tokens: int = 1
    max_max_tokens: int = 4096


def _clamp(value: float, low: float, high: float) -> float:
    """Ramène ``value`` entre ``low`` et ``high``."""
    return max(low, min(value, high))


def _is_number(value: Any) -> bool:
    """Vrai pour int et float finis, faux pour bool, inf et nan."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )tance(value, bool)


@dataclass(frozen=True)
class GenerationParams:
    """Réglages d'une requête au LLM, toujours dans les bornes.

    Requête vide : valeurs par défaut.

    >>> GenerationParams.from_request(None)
    GenerationParams(temperature=0.7, max_tokens=1024)
    >>> GenerationParams.from_request({})
    GenerationParams(temperature=0.7, max_tokens=1024)

    Valeurs hors bornes : ramenées aux bornes.

    >>> GenerationParams.from_request({"temperature": 5, "max_tokens": 999999})
    GenerationParams(temperature=2.0, max_tokens=4096)
    >>> GenerationParams.from_request({"temperature": -1, "max_tokens": 0})
    GenerationParams(temperature=0.0, max_tokens=1)

    Valeurs valides : gardées telles quelles.

    >>> GenerationParams.from_request({"temperature": 0.2, "max_tokens": 300})
    GenerationParams(temperature=0.2, max_tokens=300)

    Valeurs invalides (texte, booléen) : valeur par défaut.

    >>> GenerationParams.from_request({"temperature": "chaud", "max_tokens": True})
    GenerationParams(temperature=0.7, max_tokens=1024)

    Bornes personnalisées (par exemple venues de Settings) :

    >>> petites = ParamLimits(max_max_tokens=200)
    >>> GenerationParams.from_request({"max_tokens": 500}, petites).max_tokens
    200
    """
    temperature: float
    max_tokens: int

    @classmethod
    def from_request(
        cls,
        request: dict[str, Any] | None,
        limits: ParamLimits = ParamLimits(),
    ) -> "GenerationParams":
        """Construit les réglages à partir de la requête, bornés par ``limits``."""
        request = request or {}

        temperature = request.get("temperature")
        if _is_number(temperature):
            temperature = _clamp(float(temperature), limits.min_temperature, limits.max_temperature)
        else:
            temperature = limits.default_temperature

        max_tokens = request.get("max_tokens")
        if _is_number(max_tokens):
            max_tokens = int(_clamp(int(max_tokens), limits.min_max_tokens, limits.max_max_tokens))
        else:
            max_tokens = limits.default_max_tokens

        return cls(temperature=temperature, max_tokens=max_tokens)

    def as_api_kwargs(self) -> dict[str, float | int]:
        """Paramètres prêts à passer à client.chat.completions.create(...).

        >>> GenerationParams(temperature=0.2, max_tokens=300).as_api_kwargs()
        {'temperature': 0.2, 'max_tokens': 300}
        """
        return {"temperature": self.temperature, "max_tokens": self.max_tokens}
