import time
from contextlib import contextmanager
from typing import Callable, Iterator

# Étapes mesurées pour chaque échange (tâches 31 et 32)
STEPS: tuple[str, ...] = ("stt", "llm", "tts")


class LatencyTracker:
    """Mesure la durée de chaque étape d'un échange, en millisecondes.

    L'horloge est injectée (par défaut time.perf_counter) pour pouvoir la
    remplacer par une fausse horloge dans les tests.

    >>> temps = iter([10.0, 10.25, 20.0, 21.5])   # fausse horloge, en secondes
    >>> tracker = LatencyTracker(clock=lambda: next(temps))
    >>> with tracker.measure("stt"):
    ...     pass
    >>> with tracker.measure("llm"):
    ...     pass
    >>> tracker.as_dict()
    {'stt_ms': 250, 'llm_ms': 1500, 'tts_ms': None}

    La durée est enregistrée même si l'étape échoue :

    >>> temps = iter([0.0, 0.1])
    >>> tracker = LatencyTracker(clock=lambda: next(temps))
    >>> try:
    ...     with tracker.measure("tts"):
    ...         raise TimeoutError()
    ... except TimeoutError:
    ...     pass
    >>> tracker.as_dict()["tts_ms"]
    100

    Une étape inconnue est refusée :

    >>> LatencyTracker().measure("vision").__enter__()
    Traceback (most recent call last):
    ...
    ValueError: Étape inconnue : vision
    """

    def __init__(self, clock: Callable[[], float] = time.perf_counter) -> None:
        self.clock = clock
        self.durations_ms: dict[str, int] = {}

    @contextmanager
    def measure(self, step: str) -> Iterator[None]:
        """Chronomètre le bloc ``with`` et range la durée sous ``step``."""
        if step not in STEPS:
            raise ValueError(f"Étape inconnue : {step}")
        start = self.clock()
        try:
            yield
        finally:
            self.durations_ms[step] = round((self.clock() - start) * 1000)

    def as_dict(self) -> dict[str, int | None]:
        """Les trois latences, prêtes à être renvoyées avec la réponse.

        Une étape qui n'a pas eu lieu (ex. pas de voix) vaut None.
        """
        return {f"{step}_ms": self.durations_ms.get(step) for step in STEPS}