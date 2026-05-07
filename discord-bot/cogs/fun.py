import random
import discord
from discord import app_commands
from discord.ext import commands


EIGHT_BALL_RESPONSES = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes, definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
]

JOKES = [
    ("Why don't scientists trust atoms?", "Because they make up everything!"),
    ("I told my wife she was drawing her eyebrows too high.", "She looked surprised."),
    ("Why can't you give Elsa a balloon?", "She'll let it go."),
    ("What do you call fake spaghetti?", "An impasta!"),
    ("Why did the scarecrow win an award?", "Because he was outstanding in his field."),
    ("I'm reading a book about anti-gravity.", "It's impossible to put down."),
    ("Did you hear about the mathematician who's afraid of negative numbers?", "He'll stop at nothing to avoid them."),
    ("Why do cows wear bells?", "Because their horns don't work."),
    ("What do you call cheese that isn't yours?", "Nacho cheese."),
    ("I would tell you a joke about construction…", "But I'm still working on it."),
]


class Fun(commands.Cog):
    """Fun commands to liven up the server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Roll a dice")
    @app_commands.describe(sides="Number of sides on the dice (default: 6)")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        if sides < 2:
            await interaction.response.send_message("A dice must have at least 2 sides!", ephemeral=True)
            return
        if sides > 1000:
            await interaction.response.send_message("That's too many sides! Max is 1000.", ephemeral=True)
            return
        result = random.randint(1, sides)
        embed = discord.Embed(
            title=f"d{sides} Roll",
            description=f"{interaction.user.mention} rolled a **{result}**",
            color=discord.Color.gold(),
        )
        embed.set_footer(text=f"Range: 1–{sides}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        emoji = "🪙"
        embed = discord.Embed(
            title=f"{emoji} Coin Flip",
            description=f"**{result}!**",
            color=discord.Color.yellow(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    @app_commands.describe(question="Your yes/no question")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        response = random.choice(EIGHT_BALL_RESPONSES)
        embed = discord.Embed(
            title="Magic 8-Ball",
            color=discord.Color.dark_purple(),
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="choose", description="Choose between multiple options")
    @app_commands.describe(options="Comma-separated list of options to choose from")
    async def choose(self, interaction: discord.Interaction, options: str):
        choices = [o.strip() for o in options.split(",") if o.strip()]
        if len(choices) < 2:
            await interaction.response.send_message(
                "Please provide at least 2 options separated by commas.", ephemeral=True
            )
            return
        chosen = random.choice(choices)
        embed = discord.Embed(
            title="I choose...",
            description=f"**{chosen}**",
            color=discord.Color.teal(),
        )
        embed.set_footer(text=f"From: {', '.join(choices)}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="joke", description="Get a random joke")
    async def joke(self, interaction: discord.Interaction):
        setup, punchline = random.choice(JOKES)
        embed = discord.Embed(
            title="Random Joke",
            color=discord.Color.orange(),
        )
        embed.add_field(name=setup, value=f"||{punchline}||", inline=False)
        embed.set_footer(text="Click the spoiler to reveal the punchline!")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
