# 🎬 EuthCap

**A lightweight Telegram TMDb Caption Bot.**

EuthCap searches Movies, TV Series, and Anime on TMDb and replies with a
high-quality poster and a clean, formatted caption. No database, no admin
panel, no inline keyboards — just fast, minimal, production-ready code.

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Hosting:** Vercel Serverless Functions
- **Delivery:** Telegram Webhooks (no polling)
- **Developer:** Euthle

---

## 📂 Project Structure

```
EuthCap/
│
├── api/
│   ├── index.py      # Homepage (dark UI status page)
│   └── webhook.py     # Telegram webhook handler
│
├── requirements.txt
├── vercel.json
├── .env.example
└── README.md
```

---

## 🤖 Bot Commands

| Command                | Description                          |
|-------------------------|---------------------------------------|
| `/start`                | Welcome message                      |
| `/help`                 | Same as `/start`                     |
| `/movie <name>`         | Search a movie                       |
| `/series <name>`        | Search a TV series                   |
| `/anime <name>`         | Search an anime (movie or series)    |
| `/tmdb <id>`             | Fetch by TMDb ID                     |
| `/imdb <id>`             | Fetch by IMDb ID                     |

If nothing is found, EuthCap replies:

```
❌ No results found.

Try another movie, series, anime, TMDb ID, or IMDb ID.
```

---

## 🧰 Prerequisites

1. A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
2. A TMDb v3 API key from [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
3. A [Vercel](https://vercel.com) account
4. [Vercel CLI](https://vercel.com/docs/cli) (`npm i -g vercel`) — optional but recommended

---

## ⚙️ Installation (Local)

```bash
git clone <your-repo-url> EuthCap
cd EuthCap
pip install -r requirements.txt
```

Copy the example environment file and fill in your keys:

```bash
cp .env.example .env
```

```
BOT_TOKEN=your_telegram_bot_token
TMDB_API_KEY=your_tmdb_api_key
WEBHOOK_SECRET=optional_random_string
```

To run it locally for testing (requires `uvicorn`):

```bash
pip install uvicorn
uvicorn api.webhook:app --reload --port 8000
```

Note: local runs won't receive real Telegram updates unless you expose the
port publicly (e.g. via `ngrok`) and set the webhook to that URL.

---

## 🚀 Vercel Deployment

### Option A — Vercel Dashboard

1. Push this project to a GitHub/GitLab/Bitbucket repository.
2. Go to [vercel.com/new](https://vercel.com/new) and import the repo.
3. In **Project Settings → Environment Variables**, add:
   - `BOT_TOKEN`
   - `TMDB_API_KEY`
   - `WEBHOOK_SECRET` (optional)
4. Deploy.

### Option B — Vercel CLI

```bash
vercel login
vercel --prod
```

Then add your environment variables:

```bash
vercel env add BOT_TOKEN
vercel env add TMDB_API_KEY
vercel env add WEBHOOK_SECRET
```

Redeploy after adding env vars:

```bash
vercel --prod
```

Your deployment URL will look like:

```
https://euthcap.vercel.app
```

Opening it in a browser shows the EuthCap status page.

---

## 🔗 Telegram Bot Setup

1. Message [@BotFather](https://t.me/BotFather) → `/newbot` → follow the
   prompts to get your `BOT_TOKEN`.
2. (Optional) Set a description, profile picture, and command list via
   `/setdescription` and `/setcommands`.

Suggested `/setcommands` list:

```
start - Welcome message
help - Show available commands
movie - Search a movie
series - Search a TV series
anime - Search an anime
tmdb - Fetch by TMDb ID
imdb - Fetch by IMDb ID
```

---

## 🎞 TMDb API Setup

1. Create an account at [themoviedb.org](https://www.themoviedb.org).
2. Go to **Settings → API** and request a **v3 API key**.
3. Use that key as `TMDB_API_KEY`.

---

## 🔑 Environment Variables

| Variable         | Required | Description                                              |
|-------------------|----------|------------------------------------------------------------|
| `BOT_TOKEN`       | ✅        | Telegram bot token from @BotFather                       |
| `TMDB_API_KEY`    | ✅        | TMDb v3 API key                                            |
| `WEBHOOK_SECRET`  | ❌        | Optional shared secret to verify webhook requests         |

---

## 🌐 Webhook Setup

Once deployed, point Telegram at your webhook endpoint:

```bash
curl -F "url=https://YOUR-DOMAIN.vercel.app/api/webhook" \
     -F "secret_token=YOUR_WEBHOOK_SECRET" \
     https://api.telegram.org/bot<BOT_TOKEN>/setWebhook
```

Omit `secret_token` if you didn't set `WEBHOOK_SECRET`.

To verify it's set correctly:

```bash
curl https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo
```

---

## 💬 Usage Examples

```
/movie Perfect Crown
/series Breaking Bad
/anime Demon Slayer
/tmdb 550
/imdb tt0111161
```

Example reply:

```
Perfect Crown (S1) (2026)

╭───────────────────
➥ Status: Returning Series
➥ Episodes: 12
➥ Ratings: 7.8 ⭐
➥ Pixels: 480p | 720p | 1080p
➥ Audio: Hindi & Korean
├───────────────────
➥ Genres: Comedy, Drama
╰───────────────────

≡ In a modern Korea with a constitutional monarchy, a Chaebol heiress and
a powerless prince enter a contract marriage, discovering love and courage
as they confront social barriers and personal scars.

𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐁𝐲 @EuthGram
```

---

Made By **Euthle**
