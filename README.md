# Minecraft RCON Bot

This bot allows managing Minecraft server using RCON through discord. App commands.

## Configuration

1. **Set up your environment variables:**
2.  - Set the Minecraft server IP and port in `config.py`:
     ```python
     IP = "82.165.63.11"    # IP address of the Minecraft server
     PORT = 25565           # Port number of the Minecraft server
     ```
   - Create a `.env` file in the same directory as `config.py`.
   - Add the following entries with your specific details:
     ```env
     DISCORD_TOKEN=your_discord_token
     RCON_PASSWORD=your_rcon_password
     RCON_PORT=25575  # Default is 25575; change if different
     RCON_HOST=your_rcon_host
     ```
     
3. **Optional:** If you do not want to use the `.env` file for any reason, you can hardcode the values directly in `config.py`.

4. **Admin Roles:**
   - Admin roles are managed through `admin_roles.json`.
   - Update this file to include the role IDs that should have administrative privileges with `/roles add`, `/roles remove` and `/roles view`.

## Commands

### Admin Roles
- **/addadmin [role_id]** - Add a role ID to the list of admin roles.
- **/removeadmin [role_id]** - Remove a role ID from the list of admin roles.
- **/viewadmins** - View all admin role IDs.

### Server User Commands
- **/status** - Get the server status.
- **/banlist** - View the list of banned players.
- **/seed** - Get the world seed.

### Administration Commands
- **/give [item] [amount] [player]** - Give items to a player.
- **/xp [amount] [player]** - Give experience points to a player.
- **/time [day|night]** - Set the time of day.
- **/weather [clear|rain|thunder]** - Set the weather.
- **/ban [player] [reason]** - Ban a player.
- **/unban [player]** - Unban a player.
- **/kick [player] [reason]** - Kick a player from the server.
- **/advancement [player] [advancement]** - Give an advancement to a player.
- **/difficulty [difficulty]** - Set the game difficulty.
- **/effect [player] [effect] [duration] [amplifier]** - Apply an effect to a player.
- **/summon [entity] [x] [y] [z]** - Summon an entity at specified coordinates.
- **/kill [player]** - Kill a player.
- **/list** - List all players online.
- **/locate [structure]** - Locate a structure in the world.
- **/reload** - Reload server configurations.
- **/setworldspawn [x] [y] [z]** - Set the world spawn point.
- **/teleport [player] [x] [y] [z]** - Teleport a player to specified coordinates.

For anything you wish to be added, let me know :)
