# Jarvis API Contract

Version: 0.1 (draft). This document is the source of truth shared by backend and frontend.
Any change to a route, schema or event must update this file in the same PR.

## General rules

- Base path: `/api`. The Vite dev server proxies `/api` to the backend.
- Format: JSON (UTF-8), except `/api/transcribe` (multipart) and `/api/chat` (SSE response).
- No authentication in v0.1 (local use). Provider keys live only in the backend `.env`.
- The conversation history is kept server-side, per `conversation_id`, in memory.
- Personal data (voice, images) is never written to disk or logged in raw form.

## Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness check |
| POST | `/api/chat` | Send a message, receive the reply as an SSE stream |
| GET | `/api/conversations/{id}` | Get the visible history of a conversation |
| DELETE | `/api/conversations/{id}` | Clear a conversation ("New conversation") |
| POST | `/api/transcribe` | Speech-to-text for a recorded audio message |
| POST | `/api/speech` | Text-to-speech. **Reserved, not implemented** (TTS on hold, see JAR-02) |

### GET /api/health

Response `200`:

```json
{ "status": "ok" }
```

### POST /api/chat

Request (`application/json`):

```json
{
  "conversation_id": "string | null",
  "text": "string",
  "image": "string | null"
}
```

- `conversation_id`: omit or `null` to start a new conversation. The server returns the id in the first event.
- `text`: required, 1 to 4000 characters (the transcription for voice messages).
- `image`: optional data URL, e.g. `data:image/jpeg;base64,...`. Allowed types: `image/jpeg`, `image/png`. Max 4 MB after base64 encoding.

Response `200` (`text/event-stream`). Events, in order:

```
event: meta
data: {"conversation_id": "c_123"}

event: token
data: {"text": "Ahoy "}

event: token
data: {"text": "moussaillon"}

event: done
data: {"text": "Ahoy moussaillon", "usage": {"prompt_tokens": 120, "completion_tokens": 45}}
```

| Event | Payload | Notes |
|---|---|---|
| `meta` | `conversation_id` | Sent once, first |
| `token` | `text` (fragment) | Sent many times. Concatenate to rebuild the reply |
| `done` | `text` (full reply), `usage` | Always the last event on success. The full text is what gets stored in the history |
| `error` | `code`, `message` | Sent instead of `done` if the failure happens after the stream started |

Errors that happen before the stream starts use a normal HTTP error (see Errors).

Frontend note: `EventSource` only supports GET, so the frontend must read this stream with `fetch` and a `ReadableStream`.

### GET /api/conversations/{id}

Response `200`:

```json
{
  "conversation_id": "c_123",
  "messages": [
    { "role": "user", "text": "Hello", "has_image": false },
    { "role": "assistant", "text": "Ahoy!", "has_image": false }
  ]
}
```

The system prompt is never returned. Images are not returned, only the `has_image` flag.
Unknown id: `404 not_found`.

### DELETE /api/conversations/{id}

Response `204` (no body). Unknown id: `404 not_found`.

### POST /api/transcribe

Request (`multipart/form-data`):

- `audio`: file, WAV, max 10 MB.
- `language`: optional, default `fr`.

Response `200`:

```json
{ "text": "Bonjour Jarvis" }
```

The frontend shows this text in the user's bubble, then sends it through `/api/chat`.

### POST /api/speech (reserved)

Not implemented in v0.1. It will return `501 not_implemented` until a TTS provider is chosen.

## Errors

All HTTP errors use the same body:

```json
{ "error": { "code": "rate_limited", "message": "Human-readable message in English." } }
```

| HTTP | `code` | When |
|---|---|---|
| 400 | `invalid_request` | Missing or malformed field, empty text, unsupported image type |
| 404 | `not_found` | Unknown `conversation_id` |
| 413 | `payload_too_large` | Image or audio over the limit |
| 429 | `rate_limited` | Provider quota exceeded |
| 501 | `not_implemented` | Reserved routes |
| 502 | `provider_error` | Provider rejected the call (invalid key, bad response) |
| 503 | `provider_unavailable` | Network failure or provider down |
| 504 | `timeout` | Provider did not answer in time |
| 500 | `internal_error` | Unexpected server error. No stack trace in the response |

The same `code` values are used in the SSE `error` event. The frontend maps each code to a clear message and never shows raw traces.

## Limits (v0.1)

- Text: 4000 characters per message.
- Image: 4 MB (base64), JPEG or PNG. Larger images must be resized by the frontend before sending.
- Audio: 10 MB, WAV.
- History: only the last image is kept in the context sent to the model (cost control).

## Out of scope for v0.1

Authentication, persistence of conversations, TTS, tool calling and agents (part 2).