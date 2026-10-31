from enum import Enum

import groq


# ---------- Liste des codes d'erreur (envoyés au frontend) ----------
class ErrorCode(str, Enum):
    UNKNOWN = "UNKNOWN"
    AUTH_INVALID = "AUTH_INVALID"
    RATE_LIMIT = "RATE_LIMIT"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"


# ---------- Erreurs Jarvis ----------
class JarvisError(Exception):
    """Base des erreurs Jarvis : un code stable + un message fixe pour l'utilisateur."""
    code: ErrorCode = ErrorCode.UNKNOWN
    user_message: str = "Une erreur est survenue, réessayez plus tard."

    def __init__(self) -> None:
        super().__init__(self.user_message)


class AuthError(JarvisError):
    code = ErrorCode.AUTH_INVALID
    user_message = "Clé API invalide ou accès refusé."


class RateLimitError(JarvisError):
    code = ErrorCode.RATE_LIMIT
    user_message = "Trop de requêtes, réessayez dans quelques instants."


class ProviderTimeoutError(JarvisError):
    code = ErrorCode.PROVIDER_TIMEOUT
    user_message = "Le service met trop de temps à répondre, réessayez."


class ProviderUnavailableError(JarvisError):
    code = ErrorCode.PROVIDER_UNAVAILABLE
    user_message = "Le service est injoignable, vérifiez votre connexion."


# ---------- Traduction des erreurs du provider ----------
AUTH_STATUS: frozenset[int] = frozenset({401, 403})
RATE_LIMIT_STATUS: int = 429


def from_status(status_code: int) -> JarvisError:
    """Traduit un code HTTP du provider en erreur Jarvis.

    >>> type(from_status(401)).__name__
    'AuthError'
    >>> type(from_status(403)).__name__
    'AuthError'
    >>> type(from_status(429)).__name__
    'RateLimitError'
    >>> type(from_status(503)).__name__
    'ProviderUnavailableError'
    """
    if status_code in AUTH_STATUS:
        return AuthError()
    if status_code == RATE_LIMIT_STATUS:
        return RateLimitError()
    if status_code >= 500:
        return ProviderUnavailableError()
    return JarvisError()


def translate(exc: BaseException) -> JarvisError:
    """Traduit une erreur du SDK Groq en erreur Jarvis.

    Le texte brut de l'exception d'origine n'est jamais repris.

    >>> import httpx
    >>> req = httpx.Request("POST", "https://api.groq.com")
    >>> type(translate(groq.APITimeoutError(request=req))).__name__
    'ProviderTimeoutError'
    >>> type(translate(groq.APIConnectionError(request=req))).__name__
    'ProviderUnavailableError'
    >>> erreur = translate(RuntimeError("invalid api key gsk_abc123"))
    >>> "gsk_abc123" in erreur.user_message
    False
    >>> erreur.code.value
    'UNKNOWN'
    """
    if isinstance(exc, JarvisError):
        return exc
    # Ordre important : le timeout est un cas particulier de l'erreur réseau
    if isinstance(exc, groq.APITimeoutError):
        return ProviderTimeoutError()
    if isinstance(exc, groq.APIConnectionError):
        return ProviderUnavailableError()
    if isinstance(exc, groq.APIStatusError):
        return from_status(exc.status_code)
    return JarvisError()
