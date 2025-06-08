import discord
from discord.ext import commands
from discord import app_commands
from sympy import sympify, SympifyError  # For math equation parsing

# Enable intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required for processing commands and messages

# Bot setup with intents
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # Shortcut for app commands (slash commands)

# Global dictionary for per-server data
server_data = {}

def get_server_data(guild_id):
    """Ensure the server data exists and return it."""
    if guild_id not in server_data:
        server_data[guild_id] = {
            "mochi_count": 0,
            "high_score": 0,
            "last_user_id": None,
        }
    return server_data[guild_id]


@bot.event
async def on_ready():
    print(f"Counting Mochi is online as {bot.user}")
    try:
        synced = await bot.tree.sync()  # Sync commands with Discord
        print(f"Synced {len(synced)} command(s) with Discord.")
    except Exception as e:
        print(f"Error syncing commands: {e}")


@bot.event
async def on_message(message):
    """Detects messages and counts numbers automatically."""
    if message.author.bot:
        return

    # Ensure the server data is initialized
    guild_id = message.guild.id
    data = get_server_data(guild_id)

    # Check if the message is a number or a valid math equation
    try:
        result = sympify(message.content)  # Try to parse as a math equation
        if result.is_number:
            number = int(result)
        else:
            raise ValueError
    except (SympifyError, ValueError):
        # If it's not a valid number or equation, do nothing
        return

    # Check if the number is the next in sequence
    if number == data["mochi_count"] + 1:
        # Ensure the same user doesn't count consecutively
        if message.author.id == data["last_user_id"]:
            await message.delete()  # Delete the user's message
            response = (
                f"@{message.author.display_name} ruined it at {data['mochi_count']}!! Next number is 1. "
            )
            if data["mochi_count"] > data["high_score"]:
                data["high_score"] = data["mochi_count"]
                response += f"🎉 New high score of {data['high_score']}! 🎉"
            await message.channel.send(response)
            data["mochi_count"] = 0
            data["last_user_id"] = None
            return

        # Update the count and stats
        data["mochi_count"] = number
        data["last_user_id"] = message.author.id  # Update the last user who counted

        # React with the 🍡 emoji and respond
        await message.add_reaction("🍡")
        await message.channel.send(f"{data['mochi_count']} mochi caught! 🥟")
    else:
        # Reset the count if the number is incorrect
        await message.delete()  # Delete the user's message
        response = (
            f"@{message.author.display_name} ruined it at {data['mochi_count']}!! Next number is 1. "
        )
        if data["mochi_count"] > data["high_score"]:
            data["high_score"] = data["mochi_count"]
            response += f"🎉 New high score of {data['high_score']}! 🎉"
        await message.channel.send(response)
        data["mochi_count"] = 0
        data["last_user_id"] = None

    await bot.process_commands(message)


@tree.command(name="reset", description="Reset the mochi counter.")
async def reset(interaction: discord.Interaction):
    """Resets the counter for the server."""
    guild_id = interaction.guild.id
    data = get_server_data(guild_id)
    data["mochi_count"] = 0
    data["last_user_id"] = None
    await interaction.response.send_message("The mochis have been reset! 🌀")


@tree.command(name="show_count", description="View the current mochi count.")
async def show_count(interaction: discord.Interaction):
    """Displays the current count for the server."""
    guild_id = interaction.guild.id
    data = get_server_data(guild_id)
    await interaction.response.send_message(f"The current count is {data['mochi_count']} mochis! 🥟")


@tree.command(name="leaderboard", description="View the server's high score.")
async def leaderboard(interaction: discord.Interaction):
    """Displays the high score for the server."""
    guild_id = interaction.guild.id
    data = get_server_data(guild_id)
    await interaction.response.send_message(f"The server's high score is {data['high_score']} mochis! 🎉")


@tree.command(name="invite", description="Get an invite link to add Counting Mochi to another server.")
async def invite(interaction: discord.Interaction):
    """Provides an invite link for the bot."""
    invite_url = f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=3072&scope=bot%20applications.commands"
    await interaction.response.send_message(f"Invite Counting Mochi to your server: {invite_url}")


# Run the bot
bot.run("YOUR_BOT_TOKEN")
