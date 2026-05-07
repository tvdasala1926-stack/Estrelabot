# Discord Bot

A Python Discord bot with general utility, fun, and moderation slash commands.

## Run & Operate

- `cd discord-bot && python bot.py` — run the Discord bot (managed by the "Discord Bot" workflow)
- Required secret: `DISCORD_BOT_TOKEN` — bot token from the Discord Developer Portal

## Stack

- Python 3.12
- discord.py 2.x (slash commands via `app_commands`)
- Cogs-based architecture

## Where things live

- `discord-bot/bot.py` — entry point, loads cogs, syncs slash commands
- `discord-bot/cogs/general.py` — /help, /ping, /info, /serverinfo, /userinfo
- `discord-bot/cogs/fun.py` — /roll, /coinflip, /8ball, /choose, /joke
- `discord-bot/cogs/moderation.py` — /kick, /ban, /unban, /purge, /slowmode, /warn, /warnings

## Architecture decisions

- Slash commands only (`app_commands`) — modern Discord UX, no prefix ambiguity
- Cog-based structure — each feature domain is its own file, easy to extend
- Warnings are stored in-memory per session (not persisted to DB)
- Bot syncs the command tree globally on every startup via `bot.tree.sync()`

## Product

A ready-to-use Discord bot with:
- **General**: ping, bot info, server info, user info
- **Fun**: dice rolls, coin flip, magic 8-ball, chooser, jokes
- **Moderation**: kick, ban, unban, bulk message purge, slowmode, member warnings

## Gotchas

- Slash commands can take up to 1 hour to propagate globally after first sync
- The bot needs the `bot` scope AND `applications.commands` scope when inviting
- Moderation commands require the bot to have appropriate server permissions
- Warnings are lost on bot restart — add a DB if persistence is needed

## Pointers

- See the `pnpm-workspace` skill for workspace structure (Node.js side)
- Discord Developer Portal: https://discord.com/developers/applications
