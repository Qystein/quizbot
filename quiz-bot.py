import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio
from typing import Dict, List
import random

# Configure bot
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix=",", intents=intents)

# Remove default help command
bot.remove_command('help')

class QuizGame:
    def __init__(self):
        self.available_quizzes = {}
        self.current_players = {}
        self.scores = {}
        self.load_quizzes()
    
    def load_quizzes(self):
        """Load all quiz files from the quizzes directory"""
        quiz_dir = "quizzes"  # Make sure this directory exists
        if not os.path.exists(quiz_dir):
            os.makedirs(quiz_dir)
            
        for filename in os.listdir(quiz_dir):
            if filename.endswith('.json'):
                with open(os.path.join(quiz_dir, filename), 'r') as file:
                    quiz_name = filename[:-5]  # Remove .json extension
                    self.available_quizzes[quiz_name] = json.load(file)

    async def display_top_3(self, channel):
        """Display top 3 players and their scores"""
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        
        embed = discord.Embed(title="🏆 Top 3 Players 🏆", color=discord.Color.gold())
        for i, (player, score) in enumerate(sorted_scores[:3], 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}[i]
            embed.add_field(name=f"{medal} Place", value=f"{player}: {score} points", inline=False)
        
        await channel.send(embed=embed)

quiz_game = QuizGame()

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.command(name='quiz_help')  # Changed from 'help' to 'quiz_help'
async def quiz_help(ctx):
    """Display available quizzes and instructions"""
    embed = discord.Embed(
        title="📚 Quiz Game Help",
        description="Welcome to the Quiz Game! Here are the available quizzes:",
        color=discord.Color.blue()
    )
    
    # List available quizzes
    quiz_list = "\n".join([f"• {quiz}" for quiz in quiz_game.available_quizzes.keys()])
    embed.add_field(name="Available Quizzes", value=quiz_list or "No quizzes available", inline=False)
    
    # Add instructions
    embed.add_field(
        name="How to Play",
        value=(
            "1. Use `,start` to start a new quiz\n"
            "2. Select which quiz you want to play\n"
            "3. Players have 15 seconds to join\n"
            "4. Answer questions within 5 seconds\n"
            "5. Scoring:\n"
            "   • Correct answer: +1 point\n"
            "   • Wrong answer: 0 points\n"
            "   • No answer: -1 point"
        ),
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def start(ctx):
    """Start a new quiz game"""
    if not quiz_game.available_quizzes:
        await ctx.send("No quizzes available! Please add some quiz files first.")
        return

    # Ask which quiz to play
    quiz_list = "\n".join([f"{i+1}. {quiz}" for i, quiz in enumerate(quiz_game.available_quizzes.keys())])
    embed = discord.Embed(title="Select a Quiz", description=quiz_list, color=discord.Color.green())
    await ctx.send(embed=embed)

    try:
        response = await bot.wait_for(
            'message',
            timeout=30.0,
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel
        )
        
        selected_index = int(response.content) - 1
        selected_quiz = list(quiz_game.available_quizzes.keys())[selected_index]
        quiz_data = quiz_game.available_quizzes[selected_quiz]
    except (ValueError, IndexError, TimeoutError):
        await ctx.send("Invalid selection or timeout. Please try again.")
        return

    # Player registration phase
    embed = discord.Embed(
        title="Who wants to join?",
        description="React with 👍 to join! (15 seconds to join)",
        color=discord.Color.blue()
    )
    join_message = await ctx.send(embed=embed)
    await join_message.add_reaction("👍")

    await asyncio.sleep(15)  # Wait for players to join

    # Get players who reacted - Fixed version
    join_message = await ctx.channel.fetch_message(join_message.id)
    reaction = join_message.reactions[0]
    players = []
    async for user in reaction.users():
        if not user.bot:  # Exclude bots
            players.append(user)

    if not players:
        await ctx.send("No players joined. Game cancelled.")
        return

    # Initialize scores
    quiz_game.scores = {player.name: 0 for player in players}
    
    # Start the quiz
    for question_data in quiz_data['questions']:
        # Display question
        question_embed = discord.Embed(
            title=question_data['question'],
            description="\n".join([f"{i+1}. {opt}" for i, opt in enumerate(question_data['options'])]),
            color=discord.Color.purple()
        )
        question_msg = await ctx.send(embed=question_embed)

        # Wait for answers (5 seconds)
        answers = {}
        async def collect_answer(player):
            try:
                response = await bot.wait_for(
                    'message',
                    timeout=5.0,
                    check=lambda m: m.author == player and m.channel == ctx.channel
                )
                answers[player.name] = response.content
            except asyncio.TimeoutError:
                answers[player.name] = None

        await asyncio.gather(*(collect_answer(player) for player in players))

        # Score answers
        correct_answer_index = question_data['options'].index(question_data['correct_answer']) + 1
        for player in players:
            if player.name not in answers or answers[player.name] is None:
                quiz_game.scores[player.name] -= 1  # No answer
            elif answers[player.name].strip() == str(correct_answer_index):
                quiz_game.scores[player.name] += 1  # Correct answer
            # Wrong answer = 0 points (no change needed)

        # Show correct answer
        await ctx.send(f"Time's up! Correct answer was: {question_data['correct_answer']}")
        
        # Display top 3
        await quiz_game.display_top_3(ctx.channel)
        
        await asyncio.sleep(2)  # Brief pause between questions

    # Final results
    final_embed = discord.Embed(title="🎮 Game Over! Final Scores 🎮", color=discord.Color.gold())
    for player, score in sorted(quiz_game.scores.items(), key=lambda x: x[1], reverse=True):
        final_embed.add_field(name=player, value=f"{score} points", inline=False)
    await ctx.send(embed=final_embed)

def create_example_quiz():
    """Create an example quiz if none exists"""
    if not os.path.exists("quizzes"):
        os.makedirs("quizzes")
        
    example_quiz = {
        "questions": [
            {
                "question": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correct_answer": "Paris"
            },
            {
                "question": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4"
            }
        ]
    }
    
    quiz_path = os.path.join("quizzes", "example_quiz.json")
    if not os.path.exists(quiz_path):
        with open(quiz_path, "w") as f:
            json.dump(example_quiz, f, indent=4)

def load_token():
    """Load token from token.txt file"""
    try:
        with open('token.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: token.txt file not found!")
        print("Please create a token.txt file with your bot token.")
        exit(1)
    except Exception as e:
        print(f"Error reading token file: {e}")
        exit(1)

if __name__ == "__main__":
    # Initialize quiz game
    quiz_game = QuizGame()
    
    # Create example quiz if none exists
    create_example_quiz()
    
    # Load token and run bot
    token = load_token()
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("Error: Invalid token! Please check your token.txt file.")
    except Exception as e:
        print(f"Error starting the bot: {e}")