# Discord Quiz Bot

A customizable Discord bot for hosting quiz games in your server. Players can join quizzes, answer questions, and compete for the highest score.

## Setup

1. Create a `token.txt` file in the root directory and paste your Discord bot token
2. Make sure Python 3.8 or higher is installed
3. Run `run.bat` to start the bot

## Commands

- `,quiz_help` - Shows available quizzes and instructions
- `,start` - Starts a new quiz game

## Creating Quiz Files

Quiz files are stored in the `quizzes` folder as JSON files. Each file represents a different quiz. (I recommend using chatGPT, claude.ai or similiar services for creating .json files. just paste the "build" and what kind of quiz you want)

### Quiz File Structure
```json
{
    "questions": [
        {
            "question": "Your question here?",
            "options": [
                "Option 1",
                "Option 2",
                "Option 3",
                "Option 4"
            ],
            "correct_answer": "Option 2"
        }
    ]
}
```

### Example Quiz File (example_quiz.json)
```json
{
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
```

### Quiz File Rules
- File must be in `.json` format
- File name will be used as the quiz name (e.g., "history_quiz.json" appears as "history_quiz")
- Each question must have exactly 4 options
- The `correct_answer` must match one of the options exactly

## Game Rules

1. When a quiz starts, players have 15 seconds to join
2. Each question has a 5-second time limit
3. Scoring system:
   - Correct answer: +1 point
   - Wrong answer: 0 points
   - No answer: -1 point
4. Top 3 players are shown after each question

## File Structure

```
Quiz-bot/
├── README.md            # This file
├── requirements.txt     # Python dependencies
├── run.bat             # Start script
├── quiz-bot.py         # Main bot code
├── token.txt           # Discord bot token
└── quizzes/            # Quiz files folder
    └── example_quiz.json
```

## Setting Up Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token
5. Paste the token in `token.txt`
6. Enable these Privileged Gateway Intents:
   - PRESENCE INTENT
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT
7. Go to OAuth2 → URL Generator
8. Select scopes:
   - bot
   - applications.commands
9. Select bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Create Public Threads
   - Send Messages in Threads
   - Embed Links
   - Attach Files
   - Read Message History
   - Add Reactions
   - Use External Emojis
   - Use Application Commands

## Customizing the Bot

### Changing Timers
In `quiz-bot.py`, you can modify:
- Join timeout: Change `await asyncio.sleep(15)` in the start command
- Answer timeout: Change `timeout=5.0` in the collect_answer function

### Changing Scoring System
In the start command, modify these lines:
```python
if player.name not in answers or answers[player.name] is None:
    quiz_game.scores[player.name] -= 1  # No answer
elif answers[player.name].strip() == str(correct_answer_index):
    quiz_game.scores[player.name] += 1  # Correct answer
# Wrong answer = 0 points (no change needed)
```

### Adding New Features
Common places to add features:
- `QuizGame` class: Add new game mechanics
- `@bot.command()` decorators: Add new commands
- `quiz_help` command: Update help information

## Troubleshooting

1. **Bot won't start**
   - Check if token.txt exists and contains the correct token
   - Verify Python is installed and in PATH
   - Check if all requirements are installed

2. **Questions don't load**
   - Verify JSON files are properly formatted
   - Check if quizzes folder exists
   - Check file permissions

3. **Commands don't work**
   - Verify bot has correct permissions in Discord
   - Check if command prefix (,) is being used
   - Check Discord developer portal for enabled intents

## Requirements

- Python 3.8 or higher
- discord.py
- asyncio

Install requirements using:
```bash
pip install -r requirements.txt
```

## Contributing

Feel free to:
1. Add new quiz files
2. Improve the code
3. Report bugs
4. Suggest new features

## License

This project is free to use and modify. Credit appreciated but not required.
