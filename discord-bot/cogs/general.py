import time
import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
    """General utility commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all available commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Bot Commands",
            description="Here's everything I can do:",
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="General",
            value=(
                "`/help` — Show this message\n"
                "`/ping` — Check bot latency\n"
                "`/info` — Bot information\n"
                "`/serverinfo` — Server information\n"
                "`/userinfo [member]` — User information"
            ),
            inline=False,
        )
        embed.add_field(
            name="Fun",
            value=(
                "`/roll [sides]` — Roll a dice (default: d6)\n"
                "`/coinflip` — Flip a coin\n"
                "`/8ball <question>` — Ask the magic 8-ball\n"
                "`/choose <options>` — Choose between options\n"
                "`/joke` — Get a random joke"
            ),
            inline=False,
        )
        embed.add_field(
            name="Estrelas",
            value=(
                "`/estrela @membro` — Dá uma estrela a um membro\n"
                "`/tirar-estrela @membro` — Remove uma estrela de um membro\n"
                "`/minhas-estrelas` — Veja suas estrelas e posição no ranking\n"
                "`/ranking` — Ranking de estrelas do servidor"
            ),
            inline=False,
        )
        embed.add_field(
            name="Moderation",
            value=(
                "`/kick <member> [reason]` — Kick a member\n"
                "`/ban <member> [reason]` — Ban a member\n"
                "`/unban <user_id>` — Unban a user\n"
                "`/purge <amount>` — Delete messages\n"
                "`/slowmode <seconds>` — Set channel slowmode\n"
                "`/warn <member> <reason>` — Warn a member"
            ),
            inline=False,
        )
        embed.set_footer(text="Moderation commands require appropriate permissions.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="Pong!",
            description=f"Latency: **{latency}ms**",
            color=discord.Color.green() if latency < 100 else discord.Color.orange(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="Show bot information")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{self.bot.user.name}",
            description="A feature-rich Discord bot built with discord.py",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Show information about this server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        embed = discord.Embed(
            title=guild.name,
            color=discord.Color.blurple(),
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Boosts", value=str(guild.premium_subscription_count), inline=True)
        embed.add_field(
            name="Created",
            value=discord.utils.format_dt(guild.created_at, style="D"),
            inline=True,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Show information about a member")
    @app_commands.describe(member="The member to look up (defaults to you)")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        roles = [r.mention for r in member.roles if r.name != "@everyone"]

        embed = discord.Embed(
            title=str(member),
            color=member.color if member.color.value else discord.Color.blurple(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Display Name", value=member.display_name, inline=True)
        embed.add_field(name="ID", value=str(member.id), inline=True)
        embed.add_field(name="Bot", value="Yes" if member.bot else "No", inline=True)
        embed.add_field(
            name="Joined Server",
            value=discord.utils.format_dt(member.joined_at, style="D") if member.joined_at else "Unknown",
            inline=True,
        )
        embed.add_field(
            name="Account Created",
            value=discord.utils.format_dt(member.created_at, style="D"),
            inline=True,
        )
        embed.add_field(
            name=f"Roles ({len(roles)})",
            value=", ".join(roles) if roles else "No roles",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
