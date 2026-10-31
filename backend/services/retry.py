import time
from typing import Callable, TypeVar

from backend.services.services.error_translator import (
    AuthError,
    JarvisError,
    ProviderTimeoutError,
    RateLimitError,
)

T = TypeVar("T")

# Erreurs passagères : on a le droit de réessayer (critère du ticket : 429 et timeout)
RETRYABLE_ERRORS: tuple[type[JarvisError], ...] = (RateLimitError, ProviderTimeoutError)


class RetryPolicy:
    """Réessais bornés avec attente croissante (backoff exponentiel).

    - Réessaie seulement les erreurs de ``retry_on`` (par défaut : 429 et timeout).
    - Ne réessaie jamais les autres erreurs, par exemple AuthError.
    - S'arrête après ``max_attempts`` appels et relance la dernière erreur.
    - Attente entre deux appels : base_delay, puis x2 à chaque fois, plafonnée à max_delay.

    >>> pauses = []
    >>> policy = RetryPolicy(max_attempts=3, base_delay=0.5, sleep=pauses.append)

    Réussit au 3e essai après deux erreurs 429 :

    >>> appels = []
    >>> def instable():
    ...     appels.append(1)
    ...     if len(appels) < 3:
    ...         raise RateLimitError()
    ...     return "ok"
    >>> policy.run(instable)
    'ok'
    >>> len(appels)
    3
    >>> pauses
    [0.5, 1.0]

    Jamais de réessai sur AuthError :

    >>> pauses.clear()
    >>> appels.clear()
    >>> def mauvaise_cle():
    ...     appels.append(1)
    ...     raise AuthError()
    >>> try:
    ...     policy.run(mauvaise_cle)
    ... except AuthError:
    ...     print("abandon immédiat")
    abandon immédiat
    >>> len(appels), pauses
    (1, [])

    S'arrête au nombre maximum de tentatives :

    >>> appels.clear()
    >>> def toujours_timeout():
    ...     appels.append(1)
    ...     raise ProviderTimeoutError()
    >>> try:
    ...     policy.run(toujours_timeout)
    ... except ProviderTimeoutError:
    ...     print("abandon après", len(appels), "essais")
    abandon après 3 essais
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 0.5,
        max_delay: float = 8.0,
        retry_on: tuple[type[BaseException], ...] = RETRYABLE_ERRORS,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts doit être au moins 1")
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_on = retry_on
        self.sleep = sleep  # injecté : les tests n'attendent pas pour de vrai

    def delay_for(self, attempt: int) -> float:
        """Attente après l'essai numéro ``attempt`` (1, 2, 3...).

        >>> policy = RetryPolicy(base_delay=0.5, max_delay=3)
        >>> [policy.delay_for(n) for n in range(1, 6)]
        [0.5, 1.0, 2.0, 3, 3]
        """
        return min(self.base_delay * 2 ** (attempt - 1), self.max_delay)

    def run(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Appelle ``func`` et réessaie selon la politique."""
        for attempt in range(1, self.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except self.retry_on:
                if attempt == self.max_attempts:
                    raise
                self.sleep(self.delay_for(attempt))
        raise RuntimeError("inaccessible")