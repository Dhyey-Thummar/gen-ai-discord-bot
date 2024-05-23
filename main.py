from concurrent.futures import ThreadPoolExecutor
import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import requests
import json
import pyaudio
import wave
import google.generativeai as genai
import logging
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
DISCORD_TOKEN = os.getenv('TOKEN')
WIT_API_KEY = os.getenv('WIT_API_KEY')

# Configure Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Audio recording setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "test.wav"

# Initialize the bot with command prefix and intents
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

class MyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.model = genai.GenerativeModel('gemini-pro')
        self.messages = None
        self.chat = None
        self.wit_api_endpoint = 'https://api.wit.ai/dictation'
        self.wit_headers = {
            'authorization': 'Bearer ' + WIT_API_KEY,
            'Content-Type': 'audio/wav'
        }

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info(f'Logged on as {self.bot.user}!')
        logging.info(f'Connected to guilds: {self.bot.guilds}')
        messages = []
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                try:
                    async for message in channel.history(limit=1000):
                        if message.author != self.bot.user and message.author.display_name != 'Deleted User' and message.content:
                            messages.append({'author': message.author.display_name, 'content': message.content})
                except Exception as e:
                    logging.error(f"Error reading history from channel {channel.name}: {e}")

        messages = [f"{message['author']}: {message['content']}" for message in messages]
        self.messages = '\n'.join(messages)
        self.chat = self.model.start_chat()
        if self.messages:
            self.chat.send_message(content=self.messages)
        logging.info("Messages stored")

    def record_audio(self, RECORD_SECONDS, WAVE_OUTPUT_FILENAME):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        print("Listening...")
        frames = []
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("Finished recording.")
        stream.stop_stream()
        stream.close()
        audio.terminate()
        waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()

    def read_audio(self, WAVE_FILENAME):
        with open(WAVE_FILENAME, 'rb') as f:
            audio = f.read()
        return audio

    def recognize_speech(self, AUDIO_FILENAME, RECORD_SECONDS):
        self.record_audio(RECORD_SECONDS, AUDIO_FILENAME)
        audio = self.read_audio(AUDIO_FILENAME)
        resp = requests.post(self.wit_api_endpoint, headers=self.wit_headers, data=audio)
        objects = resp.text.strip().split('\n}\r\n{')
        json_text = '[{}]'.format('},{'.join(objects)).replace('}{', '},{')
        json_array = json.loads(json_text)
        final_transcriptions = [item['text'] for item in json_array if item['type'] == 'FINAL_TRANSCRIPTION']
        recognized_text = ' '.join(final_transcriptions) if final_transcriptions else 'No speech detected'
        return recognized_text

    @app_commands.command(name='generate', description='Generate a response based on the input text')
    @app_commands.describe(text='The input text for the model')
    async def generate(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer()  # Defer the response
        response = self.chat.send_message(content=text)
        await interaction.followup.send(response.text)

    @app_commands.command(name='summariseme', description='Summarize the attitude of the specified user')
    async def summariseme(self, interaction: discord.Interaction):
        logging.info("Summarizing")
        await interaction.response.defer()  # Defer the response
        response = self.chat.send_message(content=f"Give the attitude of the user \"{interaction.user.display_name}\"")
        await interaction.followup.send(response.text)

    @app_commands.command(name='join', description='Join the voice channel')
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.response.send_message(f"Joined {channel}")

    @app_commands.command(name='leave', description='Leave the voice channel')
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Disconnected from the voice channel")

    @app_commands.command(name='transcribe', description='Transcribe speech from the voice channel')
    @app_commands.describe(seconds='Number of seconds to record')
    async def transcribe(self, interaction: discord.Interaction, seconds: int):
        await interaction.response.defer()
        if interaction.guild.voice_client:
            await interaction.followup.send(f"Recording for {seconds} seconds...")
            recognized_text = await self.bot.loop.run_in_executor(self.executor, self.recognize_speech, WAVE_OUTPUT_FILENAME, seconds)
            await interaction.followup.send(f"You said: {recognized_text}")
            response = self.chat.send_message(content=recognized_text)
            await interaction.followup.send(response.text)

# Register the commands and synchronize them
@bot.event
async def on_ready():
    logging.info(f'Logged on as {bot.user}!')
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} commands")
    except Exception as e:
        logging.error(f"Error syncing commands: {e}")

async def main():
    async with bot:
        await bot.add_cog(MyBot(bot))
        await bot.start(DISCORD_TOKEN)

# Run the bot
asyncio.run(main())
