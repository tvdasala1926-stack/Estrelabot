import json
import os
import discord
from discord import app_commands
from discord.ext import commands

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "estrelas.json")


def _load() -> dict:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _count_stars(nickname: str) -> int:
    return nickname.count("⭐")


def _base_name(nickname: str) -> str:
    return nickname.replace("⭐", "").strip()


class Estrelas(commands.Cog):
    """Sistema de estrelas por mérito."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="estrela", description="Dá uma estrela para um membro do servidor")
    @app_commands.describe(membro="O membro que vai receber a estrela")
    @app_commands.default_permissions(manage_nicknames=True)
    async def estrela(self, interaction: discord.Interaction, membro: discord.Member):
        if membro.bot:
            await interaction.response.send_message("Bots não podem receber estrelas.", ephemeral=True)
            return
        if membro == interaction.user:
            await interaction.response.send_message("Você não pode dar uma estrela para si mesmo.", ephemeral=True)
            return

        await interaction.response.defer()

        data = _load()
        guild_id = str(interaction.guild_id)
        user_id = str(membro.id)

        guild_data = data.setdefault(guild_id, {})
        entry = guild_data.setdefault(user_id, {"nome": membro.name, "estrelas": 0})
        entry["estrelas"] += 1
        entry["nome"] = membro.name
        total = entry["estrelas"]
        _save(data)

        base = _base_name(membro.display_name)
        novo_apelido = f"{base} {'⭐' * total}"
        try:
            await membro.edit(nick=novo_apelido)
            apelido_msg = f"Apelido atualizado para **{novo_apelido}**"
        except discord.Forbidden:
            apelido_msg = "Não foi possível editar o apelido (sem permissão sobre esse membro)"

        embed = discord.Embed(
            title="⭐ Estrela concedida!",
            color=discord.Color.gold(),
        )
        embed.add_field(name="Membro", value=membro.mention, inline=True)
        embed.add_field(name="Total de estrelas", value=f"{'⭐' * total} ({total})", inline=True)
        embed.add_field(name="Apelido", value=apelido_msg, inline=False)
        embed.set_footer(text=f"Concedida por {interaction.user}")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="ranking", description="Mostra o ranking de estrelas do servidor")
    async def ranking(self, interaction: discord.Interaction):
        data = _load()
        guild_data = data.get(str(interaction.guild_id), {})

        if not guild_data:
            await interaction.response.send_message("Nenhuma estrela foi concedida ainda neste servidor.", ephemeral=True)
            return

        sorted_members = sorted(guild_data.items(), key=lambda x: x[1]["estrelas"], reverse=True)

        embed = discord.Embed(
            title="🏆 Ranking de Estrelas",
            color=discord.Color.gold(),
        )

        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for i, (uid, info) in enumerate(sorted_members[:10]):
            prefix = medals[i] if i < 3 else f"`{i + 1}.`"
            member = interaction.guild.get_member(int(uid))
            display = member.mention if member else f"**{info['nome']}**"
            stars = info["estrelas"]
            lines.append(f"{prefix} {display} — {'⭐' * min(stars, 10)} **({stars})**")

        embed.description = "\n".join(lines)
        embed.set_footer(text=f"Top {len(lines)} membros · {interaction.guild.name}")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Estrelas(bot))
