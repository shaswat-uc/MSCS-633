"""
train_bot.py
============
Hands-On Assignment 3 (MSCS-633): Django management command that trains
the ChatterBot instance on the built-in English corpus.

Usage
-----
    python manage.py train_bot

The command reads the CHATTERBOT configuration from Django settings,
creates the bot, and feeds it the standard English-language corpus
(greetings, conversations, trivia, humour, etc.).  Training only needs
to be run once; the learned data is persisted in an SQLite database
so subsequent ``chat`` sessions start instantly.
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer


class Command(BaseCommand):
    """Train the chatbot on the built-in English corpus."""

    help = "Train the ChatterBot instance using the English corpus."

    def handle(self, *args, **options):
        """Entry point called by Django's management framework."""

        # Retrieve the bot configuration from settings.py
        bot_settings = settings.CHATTERBOT

        # Create the ChatBot instance with the configured adapters
        self.stdout.write("Creating chatbot instance...")
        chatbot = ChatBot(**bot_settings)

        # Attach the corpus trainer — this trainer reads pre-built
        # YAML conversation files bundled with chatterbot_corpus.
        trainer = ChatterBotCorpusTrainer(chatbot)

        # Train on the full English corpus.  This includes:
        #   - greetings          - conversations
        #   - trivia             - humour
        #   - history            - science
        #   - computers          - food
        #   - psychology         - and more
        self.stdout.write("Training on English corpus (this may take a moment)...")
        trainer.train("chatterbot.corpus.english")

        self.stdout.write(
            self.style.SUCCESS("Training complete! Run 'python manage.py chat' to start chatting.")
        )
