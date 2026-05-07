import discord
from discord import app_commands
from discord.ext import commands


class Moderation(commands.Cog):
    """Moderation commands for server management."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.warnings: dict[int, list[dict]] = {}

    def _mod_embed(self, title: str, color: discord.Color, **fields) -> discord.Embed:
        embed = discord.Embed(title=title, color=color)
        for name, value in fields.items():
            embed.add_field(name=name.replace("_", " ").title(), value=str(value), inline=True)
        return embed

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member == interaction.user:
            await interaction.response.send_message("You cannot kick yourself.", ephemeral=True)
            return
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You cannot kick someone with an equal or higher role.", ephemeral=True)
            return
        await member.kick(reason=f"{interaction.user} — {reason}")
        embed = self._mod_embed(
            "Member Kicked", discord.Color.orange(),
            member=str(member), reason=reason, moderator=str(interaction.user)
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for ban", delete_days="Days of messages to delete (0–7)")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided", delete_days: int = 0):
        if member == interaction.user:
            await interaction.response.send_message("You cannot ban yourself.", ephemeral=True)
            return
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You cannot ban someone with an equal or higher role.", ephemeral=True)
            return
        delete_days = max(0, min(7, delete_days))
        await member.ban(reason=f"{interaction.user} — {reason}", delete_message_days=delete_days)
        embed = self._mod_embed(
            "Member Banned", discord.Color.red(),
            member=str(member), reason=reason, moderator=str(interaction.user)
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unban", description="Unban a user by their ID")
    @app_commands.describe(user_id="The ID of the user to unban")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            uid = int(user_id)
        except ValueError:
            await interaction.response.send_message("Invalid user ID.", ephemeral=True)
            return
        try:
            user = await self.bot.fetch_user(uid)
            await interaction.guild.unban(user, reason=f"Unbanned by {interaction.user}")
            embed = self._mod_embed(
                "User Unbanned", discord.Color.green(),
                user=str(user), moderator=str(interaction.user)
            )
            await interaction.response.send_message(embed=embed)
        except discord.NotFound:
            await interaction.response.send_message("User not found or is not banned.", ephemeral=True)

    @app_commands.command(name="purge", description="Delete a number of messages from this channel")
    @app_commands.describe(amount="Number of messages to delete (1–100)")
    @app_commands.default_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        if not 1 <= amount <= 100:
            await interaction.response.send_message("Amount must be between 1 and 100.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted **{len(deleted)}** message(s).", ephemeral=True)

    @app_commands.command(name="slowmode", description="Set the slowmode delay for this channel")
    @app_commands.describe(seconds="Delay in seconds (0 to disable, max 21600)")
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        if not 0 <= seconds <= 21600:
            await interaction.response.send_message("Slowmode must be between 0 and 21600 seconds.", ephemeral=True)
            return
        await interaction.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            msg = f"Slowmode disabled in {interaction.channel.mention}."
        else:
            msg = f"Slowmode set to **{seconds}s** in {interaction.channel.mention}."
        embed = discord.Embed(description=msg, color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason for the warning")
    @app_commands.default_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if member.bot:
            await interaction.response.send_message("You cannot warn a bot.", ephemeral=True)
            return
        warnings = self.warnings.setdefault(member.id, [])
        warnings.append({"reason": reason, "moderator": str(interaction.user)})
        count = len(warnings)

        try:
            dm_embed = discord.Embed(
                title="You have been warned",
                description=f"**Server:** {interaction.guild.name}\n**Reason:** {reason}",
                color=discord.Color.orange(),
            )
            dm_embed.set_footer(text=f"Warning {count} | Moderator: {interaction.user}")
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            pass

        embed = self._mod_embed(
            "Member Warned", discord.Color.orange(),
            member=str(member), reason=reason,
            moderator=str(interaction.user), total_warnings=str(count)
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warnings", description="View a member's warnings")
    @app_commands.describe(member="Member to check")
    @app_commands.default_permissions(manage_messages=True)
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        warns = self.warnings.get(member.id, [])
        embed = discord.Embed(
            title=f"Warnings for {member}",
            color=discord.Color.orange() if warns else discord.Color.green(),
        )
        if not warns:
            embed.description = "No warnings on record."
        else:
            for i, w in enumerate(warns, 1):
                embed.add_field(
                    name=f"Warning {i}",
                    value=f"**Reason:** {w['reason']}\n**By:** {w['moderator']}",
                    inline=False,
                )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
