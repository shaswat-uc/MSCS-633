"""
chat.py
=======
Hands-On Assignment 3 (MSCS-633): Django management command that starts
an interactive terminal chat session with the trained ChatterBot.

Usage
-----
    python manage.py chat

The user types a message, the bot responds, and the loop continues
until the user types one of the exit keywords (quit, exit, bye).

Typical session::

    user: Good morning! How are you doing?
    bot:  I am doing very well, thank you for asking.
    user: You're welcome.
    bot:  Do you like hats?
    user: bye
    bot:  Goodbye! Have a great day.
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from chatterbot import ChatBot


# Words that signal the user wants to end the conversation.
EXIT_KEYWORDS = {"quit", "exit", "bye"}


class Command(BaseCommand):
    """Start an interactive terminal chat session."""

    help = "Launch the terminal Q&A chatbot."

    def handle(self, *args, **options):
        """Main loop: read user input, get a bot response, repeat."""

        # Retrieve the bot configuration from settings.py
        bot_settings = settings.CHATTERBOT
        chatbot = ChatBot(**bot_settings)

        # Print a welcome banner so the user knows the bot is ready.
        self.stdout.write(self.style.SUCCESS(
            "\n=== MSCS-633 ChatBot ===\n"
            "Type your message and press Enter.\n"
            "Type 'quit', 'exit', or 'bye' to end the session.\n"
        ))

        while True:
            try:
                # Prompt the user for input
                user_input = input("user: ").strip()
            except (EOFError, KeyboardInterrupt):
                # Handle Ctrl+C or piped-input EOF gracefully.
                self.stdout.write("\nbot:  Goodbye!")
                break

            # Skip empty lines so the bot doesn't receive blank input.
            if not user_input:
                continue

            # Check whether the user wants to leave.
            if user_input.lower() in EXIT_KEYWORDS:
                self.stdout.write("bot:  Goodbye! Have a great day.")
                break

            # Get the bot's response using ChatterBot's logic adapters.
            # The BestMatch adapter compares the input against all
            # stored statements and returns the paired response with
            # the highest confidence score.
            response = chatbot.get_response(user_input)

            # Display the response to the terminal.
            self.stdout.write(f"bot:  {response}\n")
