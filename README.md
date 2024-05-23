# Discord AI Bot

This is a Discord bot that integrates with Google's Generative AI and Wit.ai to provide text and voice-based functionalities. The bot can generate responses based on text inputs, summarize user attitudes, join and leave voice channels, and transcribe speech from voice channels.

## Features

- **Text Generation**: Generate responses based on input text using Google's Generative AI.
- **User Summarization**: Summarize the attitude of a specified user.
- **Voice Channel Interaction**: Join and leave voice channels.
- **Voice Transcription**: Transcribe speech from the voice channel using Wit.ai.

## Setup

### Prerequisites

- Python 3.8+
- Discord account and server
- Google Generative AI API key
- Wit.ai API key

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/discord-ai-bot.git
    cd discord-ai-bot
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add your API keys and bot token:
    ```env
    DISCORD_TOKEN=your-discord-bot-token
    GOOGLE_API_KEY=your-google-api-key
    WIT_API_KEY=your-wit-ai-api-key
    ```

### Usage

1. Run the bot:
    ```sh
    python bot.py
    ```

2. Add the bot to your Discord server using the OAuth2 URL generated in the Discord Developer Portal.

### Commands

- **Generate Response**:
    ```
    /generate <text>
    ```
    Generate a response based on the input text.

- **Summarize User**:
    ```
    /summariseme
    ```
    Summarize the attitude of the user who invoked the command.

- **Join Voice Channel**:
    ```
    /join
    ```
    Join the voice channel of the user who invoked the command.

- **Leave Voice Channel**:
    ```
    /leave
    ```
    Leave the current voice channel.

- **Transcribe Speech**:
    ```
    /transcribe <seconds>
    ```
    Transcribe speech from the voice channel for the specified number of seconds.

## Acknowledgements

- [Discord.py](https://discordpy.readthedocs.io/)
- [Google Generative AI](https://developers.google.com/generative-ai)
- [Wit.ai](https://wit.ai/)

## Contact

For any questions or feedback, please contact [dhyeythummar8@gmail.com](mailto:dhyeythummar8@gmail.com).
