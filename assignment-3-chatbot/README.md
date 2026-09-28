# Django ChatterBot — Terminal Q&A Chatbot

Hands-On Assignment 3 (MSCS-633): A terminal-based conversational
chatbot built with Django and ChatterBot.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run database migrations
python manage.py migrate

# 3. Train the bot (first run only — takes ~30 seconds)
python manage.py train_bot

# 4. Start chatting
python manage.py chat
```

## Project Structure

```
chatbot_project/
├── manage.py                   # Django management entry point
├── requirements.txt            # Python dependencies
├── chatbot_project/
│   ├── settings.py             # Django settings (includes ChatterBot config)
│   └── urls.py                 # URL routing
└── chatbot/
    ├── apps.py                 # App configuration
    ├── models.py               # (empty — ChatterBot manages its own DB)
    ├── management/
    │   └── commands/
    │       ├── train_bot.py    # Custom command: train the chatbot
    │       └── chat.py         # Custom command: terminal chat client
    └── views.py                # (available for future web UI)
```

## How It Works

ChatterBot uses machine-learning-based selection of responses from a
corpus of known conversations.  The bot is trained on the built-in
English corpus (greetings, conversations, trivia, etc.), then uses a
"best match" logic adapter to pick the closest matching response at
runtime.

Type `quit`, `exit`, or `bye` to end the conversation.
