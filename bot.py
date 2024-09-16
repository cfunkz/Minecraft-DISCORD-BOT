import discord
from discord.ext import commands, tasks
from discord import app_commands
from mcstatus import JavaServer
from mcrcon import MCRcon
from config import *

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def send_rcon_command(command):
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as rcon_client:
            response = rcon_client.command(command)
            return response
    except Exception as error:
        return f"Command error: {error}"

# Config for simple query


@tasks.loop(minutes=1)
async def update_status_message():
    try:
        data = await query_minecraft_server(IP, PORT)
        if data["online"]:
            player_count = data["players_online"]
            max_players = data["max_players"]
            status_message = f"{player_count}/{max_players} players online"
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=status_message))
        else:
            await bot.change_presence(activity=discord.ActivityType.playing, name="Minecraft server offline")
    
    except Exception as error:
        print(f"Error updating status: {error}")

async def query_minecraft_server(ip: str, port: int):
    try:
        server = JavaServer.lookup(f"{ip}:{port}")
        status = await server.async_status()

        if status.players.sample:
            player_names = [player.name for player in status.players.sample]
        else:
            player_names = []

        return {
            "online": True,
            "version": status.version.name,
            "players_online": status.players.online,
            "max_players": status.players.max,
            "description": status.description,
            "player_names": player_names,
            "ping": await server.async_ping(),
        }
    except Exception as error:
        print(f"Error querying the server: {error}")
        return {"online": False}

def check_admin_role(interaction):
    return any(role.id in ALLOWED_ROLE_ID for role in interaction.user.roles)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    synced = await bot.tree.sync()
    print(f"{len(synced)} commands sycned. Bot ready!")
    update_status_message.start()  # Start the status update

server_group = app_commands.Group(name="server", description="Server Commands")

@server_group.command(name="status", description="Get the status of a Minecraft server")
async def minecraft(interaction: discord.Interaction):
    print(f"Status Command: Called by {interaction.user.name}")
    await interaction.response.defer()
    data = await query_minecraft_server(IP, PORT)

    if data["online"]:
        embed = discord.Embed(
            title=f"🟢 {bot.user.name} Status",
            description=f"{IP}:{PORT} is **online**!",
            color=discord.Color.green()
        )
        ping = data['ping'] * 100
        embed.add_field(name="🌍 Version", value=data["version"], inline=True)
        embed.add_field(name="📝 Description", value=str(data["description"]), inline=False)
        embed.add_field(name="📡 Ping", value=f"{ping:.2f} ms", inline=True)

        if data["players_online"] > 0:
            players_list = data["player_names"]
            if len(players_list) > 50:
                players_list = players_list[:50] + ["...and more"]
            players_formatted = "\n".join(players_list)
            embed.add_field(name=f"👥 Players Online {data['players_online']}/{data['max_players']}", value=players_formatted, inline=False)
        else:
            embed.add_field(name=f"👥 Players Online {data['players_online']}/{data['max_players']}", value="No players online.", inline=False)

        embed.set_thumbnail(url="https://i.ibb.co/QJhHc3d/Userbox-creeper-svg.png")
        await interaction.followup.send(embed=embed)

    else:
        embed = discord.Embed(
            title=f"🔴 {bot.name} Status",
            description=f"{IP}:{PORT} is **offline**.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Server might be down or unreachable", icon_url="https://i.imgur.com/75gA21p.png")
        await interaction.followup.send(embed=embed)

@server_group.command(name="give", description="Give an item to a player")
async def give(interaction: discord.Interaction, user: str, item: str, amount: int=1):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return
    print(f"Give Command: Called by {interaction.user.name}. Given to {user}, {item}, {amount}")
    command = f"/give {user} {item} {amount}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]") or response.endswith("was found"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Item Given",
		 description=f"**Player:** {user}\n**Item:** {item}\n**Amount:** {amount}",
		 color=discord.Color.green()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)
    

@server_group.command(name="teleport", description="Teleport a player to another player")
async def teleport(interaction: discord.Interaction, player1: str, player2: str):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return
    print(f"Teleport Command: Called by {interaction.user.name}. {player1} teleported to {player2}")
    command = f"/tp {player1} {player2}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]") or response.endswith("was found"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Player Teleported",
		 description=f"**Player:** {player1}\n**Destination:** {player2}",
		 color=discord.Color.blue()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="spawn", description="Teleport a player to the spawn")
async def spawn(interaction: discord.Interaction, player: str):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return
    print(f"Spawn Command: Called by {interaction.user.name}. {user} teleported to spawn.")
    command = f"/tp {player} ~ ~ ~"
    response = send_rcon_command(command)
    if response.endswith("[HERE]") or response.endswith("was found"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Player Teleported to Spawn",
		 description=f"**Player:** {player}",
		 color=discord.Color.purple()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="kick", description="Kick a player from the server")
async def kick(interaction: discord.Interaction, player: str, reason: str):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    command = f"/kick {player} {reason}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]") or response.endswith("was found"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Player Kicked",
		 description=f"**Player:** {player}\n**Reason:** {reason}",
		 color=discord.Color.red()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="ban", description="Ban a player from the server")
async def ban(interaction: discord.Interaction, player: str, reason: str):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    command = f"/ban {player} {reason}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]") or response.endswith("was found"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Player Banned",
		 description=f"**Player:** {player}\n**Reason:** {reason}",
		 color=discord.Color.red()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="unban", description="Unban a player from the server")
async def unban(interaction: discord.Interaction, player: str):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    command = f"/pardon {player}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]") or response.endswith("was found"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Player Unbanned",
		 description=f"**Player:** {player}",
		 color=discord.Color.green()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="advancement", description="Grant or revoke an advancement")
async def advancement(interaction: discord.Interaction, action: str, player: str, advancement: str):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    if action not in ["grant", "revoke"]:
        await interaction.response.send_message("Invalid action. Use 'grant' or 'revoke'.", ephemeral=True)
        return

    command = f"/advancement {action} {player} {advancement}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]") or response.endswith("was found"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Advancement Updated",
		 description=f"**Action:** {action.capitalize()}\n**Player:** {player}\n**Advancement:** {advancement}",
		 color=discord.Color.gold()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="summon", description="Summon an entity at specified coordinates")
async def summon(interaction: discord.Interaction, entity: str, x: int, y: int, z: int):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    command = f"/summon {entity} {x} {y} {z}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Entity Summoned",
		 description=f"**Entity:** {entity}\n**Coordinates:** X:{x} Y:{y} Z:{z}",
		 color=discord.Color.orange()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)
    
@server_group.command(name="setworldspawn", description="Summon an entity at specified coordinates")
async def setspawn(interaction: discord.Interaction, x: int, y: int, z: int):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    command = f"/setworldspawn {x} {y} {z}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="World spawn set!",
		 description=f"Spawn set at Coordinates:** X:{x} Y:{y} Z:{z}",
		 color=discord.Color.green()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="weather", description="Change the weather in the game")
async def weather(interaction: discord.Interaction, weather_type: str, duration: int):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    if weather_type not in ["clear", "rain", "thunder"]:
        await interaction.response.send_message("Invalid weather type. Use 'clear', 'rain', or 'thunder'.", ephemeral=True)
        return

    command = f"/weather {weather_type} {duration}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Weather Changed",
		 description=f"**Weather Type:** {weather_type.capitalize()}\n**Duration:** {duration} seconds",
		 color=discord.Color.blue()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="time", description="Set the time of day")
async def time(interaction: discord.Interaction, time_of_day: str):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    if time_of_day not in ["day", "night", "midnight", "noon"]:
        await interaction.response.send_message("Invalid time of day. Use 'day', 'night', 'midnight', or 'noon'.", ephemeral=True)
        return

    command = f"/time set {time_of_day}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Time Set",
		 description=f"**Time of Day:** {time_of_day.capitalize()}",
		 color=discord.Color.yellow()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="effect", description="Apply or remove a status effect from a player")
async def effect(interaction: discord.Interaction, action: str, player: str, effect: str, duration: int, amplifier: int = 0):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    if action not in ["give", "clear"]:
        await interaction.response.send_message("Invalid action. Use 'give' or 'clear'.", ephemeral=True)
        return

    command = f"/effect {action} {player} {effect} {duration} {amplifier}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]") or response.endswith("was found"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Effect Applied",
		 description=f"**Action:** {action.capitalize()}\n**Player:** {player}\n**Effect:** {effect}\n**Duration:** {duration} seconds\n**Amplifier:** {amplifier}",
		 color=discord.Color.pink()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="kill", description="Kill a player or entity")
async def kill(interaction: discord.Interaction, target: str):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    command = f"/kill {target}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]") or response.endswith("was found"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Target Killed",
		 description=f"**Target:** {target}",
		 color=discord.Color.red()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)
    
@server_group.command(name="xp", description="Adds XP or LEVEL to a player")
@app_commands.describe(
    action="Action to perform (add, set, query)",
    player="Target player",
    amount="Amount of XP or Levels to add/remove",
    action2="Type to modify (points or levels)"
)
async def add_xp(
    interaction: discord.Interaction,
    action: str,
    player: str,
    amount: int,
    action2: str
):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return
        
    if action not in ["set", "add", "query"]:
        await interaction.response.send_message("Wrong type specified. Use `set`, `add` or `query`.", ephemeral=True)
        return

    if action2 not in ["points", "levels"]:
        await interaction.response.send_message("Wrong type specified. Use `points` or `levels`.", ephemeral=True)
        return

    if action2 == "points":
        command = f"/xp {action} {player} {amount} points"
    elif action2 == "levels":
        command = f"/xp {action} {player} {amount} levels"

    response = send_rcon_command(command)
    if response.endswith("[HERE]") or response.endswith("was found"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Success!",
		 description=f"**Target:** {player}\n**Action:** {action.capitalize()}\n**Amount:** {amount} {action2}",
		 color=discord.Color.green()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="locate", description="Locate a specific structure or biome")
async def locate(interaction: discord.Interaction, structure: str):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    command = f"/locate {structure}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Structure Located",
		 description=f"**Structure/Biome:** {structure}",
		 color=discord.Color.green()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="banlist", description="View the ban list")
async def banlist(interaction: discord.Interaction):
    command = "/banlist"
    response = send_rcon_command(command)
    embed = discord.Embed(
		 title="Ban List",
		 description="Viewing the ban list.",
		 color=discord.Color.blue()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="list", description="List all online players")
async def list_players(interaction: discord.Interaction):
    response = send_rcon_command("/list")

    embed = discord.Embed(
        title="Online Players",
        description="List of all online players.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="seed", description="Get the world seed")
async def seed(interaction: discord.Interaction):
    response = send_rcon_command("/seed")

    embed = discord.Embed(
        title="World Seed",
        description=f"**Seed:** {response}",
        color=discord.Color.orange()
    )
    embed.set_footer(text="World seed fetched successfully.")
    await interaction.response.send_message(embed=embed)
    
@server_group.command(name="reload", description="Reload server")
async def reload(interaction: discord.Interaction):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return
    response = send_rcon_command("/reload")
	
    embed = discord.Embed(
        title="Success!",
        description=f"{response}...\n**Server reloaded.**",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)

@server_group.command(name="difficulty", description="Change the game difficulty")
async def difficulty(interaction: discord.Interaction, level: str):
    if not check_admin_role(interaction):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    if level not in ["peaceful", "easy", "normal", "hard"]:
        await interaction.response.send_message("Wrong difficulty level. Use 'peaceful', 'easy', 'normal', or 'hard'.", ephemeral=True)
        return

    command = f"/difficulty {level}"
    response = send_rcon_command(command)
    if response.endswith("[HERE]"):
        embed = discord.Embed(
            title="Error!",
            description="The command was unsuccessful. Please check the server logs for more details.",
            color=discord.Color.red()
        )
    else:
	    embed = discord.Embed(
		 title="Difficulty Changed",
		 description=f"**New Difficulty Level:** {level.capitalize()}",
		 color=discord.Color.purple()
	    )
    embed.set_footer(text=f"Response: {response}")
    await interaction.response.send_message(embed=embed)
    
role_group = app_commands.Group(name="role", description="Add/Remove Admin Roles")

@role_group.command(name="add", description="Add a role to the admin list")
@app_commands.checks.has_permissions(moderate_members=True)
async def add_role(interaction: discord.Interaction, role: discord.Role):
    if role.id in ALLOWED_ROLE_ID:
        await interaction.response.send_message(f"Role {role.name} is already an admin role.", ephemeral=True)
    else:
        ALLOWED_ROLE_ID.append(role.id)
        ave_admin_roles(ALLOWED_ROLE_ID)
        await interaction.response.send_message(f"Role {role.name} has been added to the admin list.", ephemeral=True)

@role_group.command(name="remove", description="Remove a role from the admin list")
@app_commands.checks.has_permissions(moderate_members=True)
async def remove_role(interaction: discord.Interaction, role: discord.Role):
    if role.id in ALLOWED_ROLE_ID:
        ALLOWED_ROLE_ID.remove(role.id)
        save_admin_roles(ALLOWED_ROLE_ID)
        await interaction.response.send_message(f"Role {role.name} has been removed from the admin list.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Role {role.name} is not an admin role.", ephemeral=True)

@role_group.command(name="view", description="View Admin Roles")
async def view_roles(interaction: discord.Interaction):
    guild_roles = interaction.guild.roles
    
    # Find roles matching the IDs in ALLOWED_ROLE_ID
    roles_mentions = [f"<@&{role.id}>" for role in guild_roles if role.id in ALLOWED_ROLE_ID]
    embed = discord.Embed(
        title="Admin Roles",
        description="Roles managing minecraft server",
        color=discord.Color.blue()
    )
    if roles_mentions:
        embed.add_field(name="Admin Roles", value=', '.join(roles_mentions))
    else:
        embed.add_field(name="Admin Roles", value="No admin roles found.")

    embed.set_footer(text="Requested by " + interaction.user.name)
    embed.set_thumbnail(url="https://i.ibb.co/QJhHc3d/Userbox-creeper-svg.png")

    await interaction.response.send_message(embed=embed, ephemeral=True)
    
bot.tree.add_command(server_group)
bot.tree.add_command(role_group)
bot.run(DISCORD_TOKEN)
