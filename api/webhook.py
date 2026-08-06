"""
EuthCap - Telegram Webhook Handler
------------------------------------
Receives Telegram updates, resolves the requested title against TMDb,
and replies with the highest quality poster + a formatted caption.

No database. No inline keyboards. No admin panel.

Developer: Euthle
"""

import os
import re
from typing import Any, Optional

import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
# Optional: if set, incoming requests must carry this Telegram secret header.
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
TMDB_API = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/original"

CHANNEL_TAG = "@EuthGram"
REQUEST_TIMEOUT = 10
CAPTION_LIMIT = 1024  # Telegram's max length for a photo caption

START_TEXT = (
    "👋 Welcome to EuthCap\n\n"
    "A lightweight Telegram TMDb Caption Generator.\n\n"
    "Available Commands\n\n"
    "/movie <name>\n"
    "/series <name>\n"
    "/anime <name>\n"
    "/tmdb <id>\n"
    "/imdb <id>\n"
    "/help\n\n"
    "Made By Euthle"
)

NOT_FOUND_TEXT = (
    "❌ No results found.\n\n"
    "Try another movie, series, anime, TMDb ID, or IMDb ID."
)


# ─────────────────────────────────────────────
# TMDb helpers
# ─────────────────────────────────────────────

def tmdb_get(path: str, params: Optional[dict] = None) -> Optional[dict]:
    """GET a TMDb endpoint. Returns parsed JSON, or None on any failure."""
    try:
        query = {"api_key": TMDB_API_KEY}
        if params:
            query.update(params)
        resp = requests.get(f"{TMDB_API}{path}", params=query, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return None
        return resp.json()
    except requests.RequestException:
        return None


def search_movie(query: str) -> Optional[dict]:
    data = tmdb_get("/search/movie", {"query": query})
    results = (data or {}).get("results") or []
    return results[0] if results else None


def search_tv(query: str) -> Optional[dict]:
    data = tmdb_get("/search/tv", {"query": query})
    results = (data or {}).get("results") or []
    return results[0] if results else None


def search_anime(query: str) -> Optional[tuple]:
    """
    Search across movies + TV and prefer animation results.
    Returns a tuple of (media_type, result_dict) or None.
    """
    data = tmdb_get("/search/multi", {"query": query})
    results = (data or {}).get("results") or []
    results = [r for r in results if r.get("media_type") in ("movie", "tv")]
    if not results:
        return None

    # Prefer animation genre (id 16) or Japanese-original titles.
    def is_anime_like(r: dict) -> bool:
        return 16 in (r.get("genre_ids") or []) or r.get("original_language") == "ja"

    best = next((r for r in results if is_anime_like(r)), results[0])
    return best.get("media_type"), best


def get_movie_details(movie_id: int) -> Optional[dict]:
    return tmdb_get(f"/movie/{movie_id}")


def get_tv_details(tv_id: int) -> Optional[dict]:
    return tmdb_get(f"/tv/{tv_id}")


def find_by_imdb(imdb_id: str) -> Optional[tuple]:
    """Look up an IMDb id via TMDb's /find endpoint."""
    data = tmdb_get(f"/find/{imdb_id}", {"external_source": "imdb_id"})
    if not data:
        return None
    if data.get("movie_results"):
        return "movie", data["movie_results"][0]
    if data.get("tv_results"):
        return "tv", data["tv_results"][0]
    return None


def get_by_tmdb_id(tmdb_id: str) -> Optional[tuple]:
    """Try resolving a raw TMDb id as a movie first, then as a TV series."""
    movie = get_movie_details(tmdb_id)
    if movie and movie.get("id"):
        return "movie", movie
    tv = get_tv_details(tmdb_id)
    if tv and tv.get("id"):
        return "tv", tv
    return None


# ─────────────────────────────────────────────
# Normalization + caption building
# ─────────────────────────────────────────────

def latest_season_number(details: dict) -> int:
    """Best-effort current season number, skipping specials (season 0)."""
    seasons = details.get("seasons") or []
    numbers = [s.get("season_number", 0) for s in seasons if s.get("season_number", 0) > 0]
    if numbers:
        return max(numbers)
    return details.get("number_of_seasons") or 1


def format_audio(details: dict) -> str:
    langs = details.get("spoken_languages") or []
    names = [l.get("english_name") or l.get("name") for l in langs if l.get("english_name") or l.get("name")]
    names = [n for n in names if n]
    if not names:
        return "Multi Audio"
    return " & ".join(dict.fromkeys(names))  # de-duped, order preserved


def format_genres(details: dict) -> str:
    genres = [g.get("name") for g in (details.get("genres") or []) if g.get("name")]
    return ", ".join(genres) if genres else "N/A"


def build_caption(media_type: str, details: dict) -> tuple:
    """
    Build the fixed-layout caption for a movie or TV/anime result.
    Returns (caption_text, poster_url_or_none).
    """
    genres = format_genres(details)
    audio = format_audio(details)
    rating = round(details.get("vote_average") or 0, 1)
    overview = (details.get("overview") or "No overview available.").strip()

    poster_path = details.get("poster_path")
    poster_url = f"{IMAGE_BASE}{poster_path}" if poster_path else None

    if media_type == "tv":
        name = details.get("name") or "Unknown Title"
        year = (details.get("first_air_date") or "")[:4] or "N/A"
        season = latest_season_number(details)
        title_line = f"{name} (S{season}) ({year})"
        status = details.get("status") or "Unknown"
        episodes = details.get("number_of_episodes") or "N/A"

        body_lines = [
            "╭───────────────────",
            f"➥ Status: {status}",
            f"➥ Episodes: {episodes}",
            f"➥ Ratings: {rating} ⭐",
            "➥ Pixels: 480p | 720p | 1080p",
            f"➥ Audio: {audio}",
            "├───────────────────",
            f"➥ Genres: {genres}",
            "╰───────────────────",
        ]
    else:
        name = details.get("title") or "Unknown Title"
        year = (details.get("release_date") or "")[:4] or "N/A"
        title_line = f"{name} ({year})"
        status = details.get("status") or "Unknown"
        runtime = details.get("runtime") or "N/A"

        body_lines = [
            "╭───────────────────",
            f"➥ Status: {status}",
            f"➥ Runtime: {runtime} min",
            f"➥ Ratings: {rating} ⭐",
            "➥ Pixels: 480p | 720p | 1080p",
            f"➥ Audio: {audio}",
            "├───────────────────",
            f"➥ Genres: {genres}",
            "╰───────────────────",
        ]

    body = "\n".join(body_lines)
    footer = f"𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐁𝐲 {CHANNEL_TAG}"

    def assemble(ov: str) -> str:
        return f"{title_line}\n\n{body}\n\n≡ {ov}\n\n{footer}"

    caption = assemble(overview)

    # If the caption is too long for Telegram, shorten ONLY the overview.
    if len(caption) > CAPTION_LIMIT:
        fixed_len = len(assemble(""))
        budget = CAPTION_LIMIT - fixed_len - 1  # -1 safety margin for the ellipsis char
        if budget < 0:
            budget = 0
        trimmed = overview[:budget].rstrip()
        # Avoid cutting mid-word where possible.
        if " " in trimmed and len(trimmed) < len(overview):
            trimmed = trimmed.rsplit(" ", 1)[0]
        trimmed = trimmed.rstrip(",.;:") + "…"
        caption = assemble(trimmed)

    return caption, poster_url


# ─────────────────────────────────────────────
# Telegram helpers
# ─────────────────────────────────────────────

def send_message(chat_id: int, text: str) -> None:
    try:
        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        pass


def send_photo(chat_id: int, photo_url: str, caption: str) -> None:
    try:
        resp = requests.post(
            f"{TELEGRAM_API}/sendPhoto",
            json={"chat_id": chat_id, "photo": photo_url, "caption": caption},
            timeout=REQUEST_TIMEOUT,
        )
        # Fall back to a text-only message if Telegram rejects the photo
        # (e.g. an unreachable poster URL).
        if resp.status_code != 200:
            send_message(chat_id, caption)
    except requests.RequestException:
        send_message(chat_id, caption)


def reply_result(chat_id: int, media_type: str, details: dict) -> None:
    caption, poster_url = build_caption(media_type, details)
    if poster_url:
        send_photo(chat_id, poster_url, caption)
    else:
        send_message(chat_id, caption)


# ─────────────────────────────────────────────
# Command handling
# ─────────────────────────────────────────────

COMMAND_RE = re.compile(r"^/(\w+)(?:@[\w_]+)?(?:\s+(.*))?$", re.DOTALL)


def parse_command(text: str) -> tuple:
    match = COMMAND_RE.match(text.strip())
    if not match:
        return "", ""
    command = match.group(1).lower()
    argument = (match.group(2) or "").strip()
    return command, argument


def handle_command(chat_id: int, command: str, argument: str) -> None:
    if command in ("start", "help"):
        send_message(chat_id, START_TEXT)
        return

    if command == "movie":
        if not argument:
            send_message(chat_id, "Usage: /movie <movie name>")
            return
        result = search_movie(argument)
        if not result:
            send_message(chat_id, NOT_FOUND_TEXT)
            return
        details = get_movie_details(result["id"])
        if not details:
            send_message(chat_id, NOT_FOUND_TEXT)
            return
        reply_result(chat_id, "movie", details)
        return

    if command == "series":
        if not argument:
            send_message(chat_id, "Usage: /series <series name>")
            return
        result = search_tv(argument)
        if not result:
            send_message(chat_id, NOT_FOUND_TEXT)
            return
        details = get_tv_details(result["id"])
        if not details:
            send_message(chat_id, NOT_FOUND_TEXT)
            return
        reply_result(chat_id, "tv", details)
        return

    if command == "anime":
        if not argument:
            send_message(chat_id, "Usage: /anime <anime name>")
            return
        found = search_anime(argument)
        if not found:
            send_message(chat_id, NOT_FOUND_TEXT)
            return
        media_type, result = found
        details = get_movie_details(result["id"]) if media_type == "movie" else get_tv_details(result["id"])
        if not details:
            send_message(chat_id, NOT_FOUND_TEXT)
            return
        reply_result(chat_id, media_type, details)
        return

    if command == "tmdb":
        if not argument or not argument.strip().isdigit():
            send_message(chat_id, "Usage: /tmdb <tmdb id>")
            return
        found = get_by_tmdb_id(argument.strip())
        if not found:
            send_message(chat_id, NOT_FOUND_TEXT)
            return
        media_type, details = found
        reply_result(chat_id, media_type, details)
        return

    if command == "imdb":
        if not argument:
            send_message(chat_id, "Usage: /imdb <imdb id>")
            return
        found = find_by_imdb(argument.strip())
        if not found:
            send_message(chat_id, NOT_FOUND_TEXT)
            return
        media_type, result = found
        details = get_movie_details(result["id"]) if media_type == "movie" else get_tv_details(result["id"])
        if not details:
            send_message(chat_id, NOT_FOUND_TEXT)
            return
        reply_result(chat_id, media_type, details)
        return

    # Unknown command: quietly point the user to /help.
    send_message(chat_id, "Unknown command. Send /help to see available commands.")


# ─────────────────────────────────────────────
# Webhook endpoint
# ─────────────────────────────────────────────

@app.post("/api/webhook")
async def telegram_webhook(request: Request) -> JSONResponse:
    """Entry point Telegram calls for every update."""
    if WEBHOOK_SECRET:
        header = request.headers.get("x-telegram-bot-api-secret-token", "")
        if header != WEBHOOK_SECRET:
            return JSONResponse({"ok": False}, status_code=401)

    try:
        update: dict[str, Any] = await request.json()
    except Exception:
        return JSONResponse({"ok": True})  # never crash on a bad payload

    message = update.get("message") or update.get("edited_message")
    if not message:
        return JSONResponse({"ok": True})

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text") or ""

    if not chat_id or not text.startswith("/"):
        return JSONResponse({"ok": True})

    command, argument = parse_command(text)
    if not command:
        return JSONResponse({"ok": True})

    try:
        handle_command(chat_id, command, argument)
    except Exception:
        # Absolute last line of defense: never let the bot crash on an update.
        send_message(chat_id, NOT_FOUND_TEXT)

    return JSONResponse({"ok": True})
