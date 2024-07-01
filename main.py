import discord
from discord.ext import commands
import asyncio
import re

# Define the intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

# Create an instance of the bot with the specified intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Event listener when the bot has switched from offline to online
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

# Function to parse duration with format like '60s', '2m', etc.
def parse_duration(duration_str):
    if not duration_str:
        return None

    match = re.match(r'^(\d+)([smh]?)$', duration_str.lower())
    if match:
        amount = int(match.group(1))
        unit = match.group(2)

        if unit == 's':
            return amount
        elif unit == 'm':
            return amount * 60
        elif unit == 'h':
            return amount * 3600

    return None

# Poll command with custom time duration
@bot.command(name='poll')
async def poll(ctx, duration_str: str, *, question_and_options: str):
    duration = parse_duration(duration_str)
    if duration is None:
        await ctx.send('Invalid duration format. Please use format like `60s`, `2m`, `1h`.')
        return

    options = question_and_options.split(',')
    if len(options) < 2:
        await ctx.send('Please provide a question and at least two options.')
        return

    question = options[0].strip()
    choices = [option.strip() for option in options[1:]]

    if len(choices) > 10:
        await ctx.send('You can only provide up to 10 options.')
        return

    if duration <= 0:
        await ctx.send('Please provide a positive duration for the poll.')
        return

    # Create the poll embed with a cyan color
    embed = discord.Embed(title=question, description='\n'.join([f'{i+1}. {choice}' for i, choice in enumerate(choices)]), color=discord.Color.from_rgb(0, 255, 255))
    embed.set_footer(text=f'Poll created by {ctx.author.display_name} | Poll closes in {duration} seconds')

    poll_message = await ctx.send(embed=embed)

    # Add reactions for voting
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    for i in range(len(choices)):
        await poll_message.add_reaction(reactions[i])

    # Countdown timer
    for remaining in range(duration, 0, -1):
        embed.set_footer(text=f'Poll created by {ctx.author.display_name} | Poll closes in {remaining} seconds')
        await poll_message.edit(embed=embed)
        await asyncio.sleep(1)

    # Update footer to indicate poll is closed
    embed.set_footer(text=f'Poll created by {ctx.author.display_name} | Poll is now closed.')
    await poll_message.edit(embed=embed)

    # Fetch the message again to get the latest state with reactions
    poll_message = await ctx.channel.fetch_message(poll_message.id)

    reaction_counts = {}
    for reaction in poll_message.reactions:
        if reaction.emoji in reactions:
            reaction_counts[reaction.emoji] = reaction.count - 1  # Subtract one for the bot's own reaction

    # Determine the winner
    if reaction_counts:
        winner_emoji = max(reaction_counts, key=reaction_counts.get)
        winner_index = reactions.index(winner_emoji)
        winner_choice = choices[winner_index]
        
        # Create the result embed with a green color
        result_embed = discord.Embed(title="Poll Results", description=f"The winning choice is:\n\n**{winner_choice}**\n\nwith **{reaction_counts[winner_emoji]}** votes.", color=discord.Color.green())
        result_embed.set_footer(text='Thank you for participating!')
        
        # Reply with the poll results
        await ctx.send(embed=result_embed)
    else:
        await ctx.send('The poll is now closed. No votes were cast.')

# Run the bot with the token
bot.run('MTI1NzI3Nzk2NjA4NjQzODk2Mw.Gk4s8Q.N0FtgWYPxg_iPaOWYjjktpRZneCxxGkj7zl-Sg')
