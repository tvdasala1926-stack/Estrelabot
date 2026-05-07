import json
import os
import discord
from discord import app_commands
from discord.ext import commands

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "estrelas.json")
LOG_CHANNEL = "logs-estrelas"


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


def _base_name(nickname: str) -> str:
    return nickname.replace("⭐", "").strip()


async def _send_log(guild: discord.Guild, embed: discord.Embed) -> None:
    channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL)
    if channel:
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            pass


class ConfirmacaoView(discord.ui.View):
    def __init__(self, membro: discord.Member, moderador: discord.Member):
        super().__init__(timeout=30)
        self.membro = membro
        self.moderador = moderador

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.moderador.id:
            await interaction.response.send_message(
                "Só quem usou o comando pode confirmar.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        self.stop()

        data = _load()
        guild_id = str(interaction.guild_id)
        user_id = str(self.membro.id)
        guild_data = data.get(guild_id, {})
        entry = guild_data.get(user_id)

        if not entry or entry["estrelas"] <= 0:
            await interaction.response.edit_message(
                content=f"❌ {self.membro.mention} não tem estrelas para remover.",
                embed=None,
                view=self,
            )
            return

        entry["estrelas"] -= 1
        total = entry["estrelas"]
        _save(data)

        base = _base_name(self.membro.display_name)
        novo_apelido = f"{base} {'⭐' * total}".strip() if total > 0 else base
        try:
            await self.membro.edit(nick=novo_apelido if novo_apelido != self.membro.name else None)
            apelido_msg = f"Apelido atualizado para **{novo_apelido or self.membro.name}**"
        except discord.Forbidden:
            apelido_msg = "Não foi possível editar o apelido (sem permissão sobre esse membro)"

        embed = discord.Embed(title="🗑️ Estrela removida", color=discord.Color.red())
        embed.add_field(name="Membro", value=self.membro.mention, inline=True)
        embed.add_field(
            name="Estrelas restantes",
            value=f"{'⭐' * total} ({total})" if total > 0 else "Nenhuma",
            inline=True,
        )
        embed.add_field(name="Apelido", value=apelido_msg, inline=False)
        embed.set_footer(text=f"Removida por {interaction.user}")
        await interaction.response.edit_message(content=None, embed=embed, view=self)

        log_embed = discord.Embed(title="🗑️ Estrela removida", color=discord.Color.red())
        log_embed.add_field(name="Membro", value=self.membro.mention, inline=True)
        log_embed.add_field(name="Removida por", value=interaction.user.mention, inline=True)
        log_embed.add_field(
            name="Total atual",
            value=f"{'⭐' * total} ({total})" if total > 0 else "Nenhuma",
            inline=True,
        )
        log_embed.timestamp = discord.utils.utcnow()
        await _send_log(interaction.guild, log_embed)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        self.stop()
        await interaction.response.edit_message(
            content="❌ Operação cancelada.", embed=None, view=self
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class ResetarView(discord.ui.View):
    def __init__(self, membro: discord.Member, moderador: discord.Member, total_atual: int):
        super().__init__(timeout=30)
        self.membro = membro
        self.moderador = moderador
        self.total_atual = total_atual

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.moderador.id:
            await interaction.response.send_message(
                "Só quem usou o comando pode confirmar.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Resetar", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        self.stop()

        data = _load()
        guild_id = str(interaction.guild_id)
        user_id = str(self.membro.id)
        guild_data = data.setdefault(guild_id, {})
        if user_id in guild_data:
            guild_data[user_id]["estrelas"] = 0
        _save(data)

        base = _base_name(self.membro.display_name)
        try:
            await self.membro.edit(nick=base if base != self.membro.name else None)
            apelido_msg = f"Apelido atualizado para **{base or self.membro.name}**"
        except discord.Forbidden:
            apelido_msg = "Não foi possível editar o apelido (sem permissão sobre esse membro)"

        embed = discord.Embed(title="🔄 Estrelas resetadas", color=discord.Color.dark_red())
        embed.add_field(name="Membro", value=self.membro.mention, inline=True)
        embed.add_field(name="Estrelas removidas", value=str(self.total_atual), inline=True)
        embed.add_field(name="Apelido", value=apelido_msg, inline=False)
        embed.set_footer(text=f"Resetado por {interaction.user}")
        await interaction.response.edit_message(content=None, embed=embed, view=self)

        log_embed = discord.Embed(title="🔄 Estrelas resetadas", color=discord.Color.dark_red())
        log_embed.add_field(name="Membro", value=self.membro.mention, inline=True)
        log_embed.add_field(name="Resetado por", value=interaction.user.mention, inline=True)
        log_embed.add_field(name="Estrelas removidas", value=str(self.total_atual), inline=True)
        log_embed.timestamp = discord.utils.utcnow()
        await _send_log(interaction.guild, log_embed)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        self.stop()
        await interaction.response.edit_message(
            content="❌ Operação cancelada.", embed=None, view=self
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class Estrelas(commands.Cog):
    """Sistema de estrelas por mérito."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="estrela", description="Dá uma estrela para um membro do servidor")
    @app_commands.describe(membro="O membro que vai receber a estrela")
    @app_commands.default_permissions(administrator=True)
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

        embed = discord.Embed(title="⭐ Estrela concedida!", color=discord.Color.gold())
        embed.add_field(name="Membro", value=membro.mention, inline=True)
        embed.add_field(name="Total de estrelas", value=f"{'⭐' * total} ({total})", inline=True)
        embed.add_field(name="Apelido", value=apelido_msg, inline=False)
        embed.set_footer(text=f"Concedida por {interaction.user}")
        await interaction.followup.send(embed=embed)

        log_embed = discord.Embed(title="⭐ Estrela concedida", color=discord.Color.gold())
        log_embed.add_field(name="Membro", value=membro.mention, inline=True)
        log_embed.add_field(name="Concedida por", value=interaction.user.mention, inline=True)
        log_embed.add_field(
            name="Total atual", value=f"{'⭐' * min(total, 10)} ({total})", inline=True
        )
        log_embed.timestamp = discord.utils.utcnow()
        await _send_log(interaction.guild, log_embed)

    @app_commands.command(name="tirar-estrela", description="Remove uma estrela de um membro")
    @app_commands.describe(membro="O membro que vai perder a estrela")
    @app_commands.default_permissions(manage_nicknames=True)
    async def tirar_estrela(self, interaction: discord.Interaction, membro: discord.Member):
        if membro.bot:
            await interaction.response.send_message("Bots não têm estrelas.", ephemeral=True)
            return

        data = _load()
        guild_data = data.get(str(interaction.guild_id), {})
        entry = guild_data.get(str(membro.id))
        total_atual = entry["estrelas"] if entry else 0

        if total_atual <= 0:
            await interaction.response.send_message(
                f"{membro.mention} não tem nenhuma estrela para remover.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="⚠️ Confirmar remoção de estrela",
            description=(
                f"Tem certeza que quer remover uma estrela de {membro.mention}?\n\n"
                f"Estrelas atuais: {'⭐' * total_atual} **({total_atual})**\n"
                f"Após a remoção: {'⭐' * (total_atual - 1)} **({total_atual - 1})**"
                if total_atual > 1
                else f"Tem certeza que quer remover a última estrela de {membro.mention}?"
            ),
            color=discord.Color.orange(),
        )
        embed.set_footer(text="Esta ação expira em 30 segundos.")

        view = ConfirmacaoView(membro=membro, moderador=interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="resetar-estrelas", description="Zera todas as estrelas de um membro e remove os ⭐ do apelido")
    @app_commands.describe(membro="O membro que terá as estrelas zeradas")
    @app_commands.default_permissions(administrator=True)
    async def resetar_estrelas(self, interaction: discord.Interaction, membro: discord.Member):
        if membro.bot:
            await interaction.response.send_message("Bots não têm estrelas.", ephemeral=True)
            return

        data = _load()
        guild_data = data.get(str(interaction.guild_id), {})
        entry = guild_data.get(str(membro.id))
        total_atual = entry["estrelas"] if entry else 0

        if total_atual <= 0:
            await interaction.response.send_message(
                f"{membro.mention} já não tem nenhuma estrela.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="⚠️ Confirmar reset de estrelas",
            description=(
                f"Tem certeza que quer **zerar todas as estrelas** de {membro.mention}?\n\n"
                f"Estrelas atuais: {'⭐' * min(total_atual, 10)} **({total_atual})**\n"
                f"Após o reset: **0 estrelas** e ⭐ removidos do apelido."
            ),
            color=discord.Color.dark_red(),
        )
        embed.set_footer(text="Esta ação expira em 30 segundos.")

        view = ResetarView(membro=membro, moderador=interaction.user, total_atual=total_atual)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="perfil", description="Mostra o perfil completo de um membro com estrelas e informações")
    @app_commands.describe(membro="O membro a consultar (padrão: você mesmo)")
    async def perfil(self, interaction: discord.Interaction, membro: discord.Member = None):
        membro = membro or interaction.user

        data = _load()
        guild_data = data.get(str(interaction.guild_id), {})
        user_id = str(membro.id)
        entry = guild_data.get(user_id)
        total = entry["estrelas"] if entry else 0

        sorted_members = sorted(
            [(uid, info) for uid, info in guild_data.items() if info["estrelas"] > 0],
            key=lambda x: x[1]["estrelas"],
            reverse=True,
        )
        posicao = next((i + 1 for i, (uid, _) in enumerate(sorted_members) if uid == user_id), None)

        roles = [r.mention for r in membro.roles if r.name != "@everyone"]

        embed = discord.Embed(
            title=f"{'⭐ ' if total > 0 else ''}Perfil de {membro.display_name}",
            color=discord.Color.gold() if total > 0 else discord.Color.blurple(),
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.add_field(
            name="⭐ Estrelas",
            value=f"{'⭐' * min(total, 10)} **({total})**" if total > 0 else "Nenhuma",
            inline=True,
        )
        embed.add_field(
            name="🏆 Ranking",
            value=f"**#{posicao}** de {len(sorted_members)}" if posicao else "Fora do ranking",
            inline=True,
        )
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(
            name="📅 Entrou no servidor",
            value=discord.utils.format_dt(membro.joined_at, style="D") if membro.joined_at else "Desconhecido",
            inline=True,
        )
        embed.add_field(
            name="🎂 Conta criada em",
            value=discord.utils.format_dt(membro.created_at, style="D"),
            inline=True,
        )
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(
            name=f"🎭 Cargos ({len(roles)})",
            value=", ".join(roles) if roles else "Nenhum cargo",
            inline=False,
        )

        if posicao == 1 and total > 0:
            embed.set_footer(text="👑 Líder do ranking de estrelas!")
        elif total == 0:
            embed.set_footer(text="Este membro ainda não tem estrelas.")
        else:
            acima = sorted_members[posicao - 2]
            faltam = acima[1]["estrelas"] - total
            nome_acima = interaction.guild.get_member(int(acima[0]))
            nome_acima = nome_acima.display_name if nome_acima else acima[1]["nome"]
            embed.set_footer(text=f"Faltam {faltam} estrela(s) para superar {nome_acima}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="minhas-estrelas", description="Veja suas estrelas e sua posição no ranking")
    async def minhas_estrelas(self, interaction: discord.Interaction):
        data = _load()
        guild_data = data.get(str(interaction.guild_id), {})
        user_id = str(interaction.user.id)
        entry = guild_data.get(user_id)
        total = entry["estrelas"] if entry else 0

        sorted_members = sorted(
            [(uid, info) for uid, info in guild_data.items() if info["estrelas"] > 0],
            key=lambda x: x[1]["estrelas"],
            reverse=True,
        )
        posicao = next((i + 1 for i, (uid, _) in enumerate(sorted_members) if uid == user_id), None)

        embed = discord.Embed(
            title="⭐ Suas Estrelas",
            color=discord.Color.gold() if total > 0 else discord.Color.greyple(),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(
            name="Total",
            value=f"{'⭐' * min(total, 10)} **({total})**" if total > 0 else "Nenhuma ainda",
            inline=True,
        )
        embed.add_field(
            name="Posição no ranking",
            value=f"**#{posicao}** de {len(sorted_members)}" if posicao else "Fora do ranking",
            inline=True,
        )
        if total == 0:
            embed.set_footer(text="Peça a um administrador para te dar uma estrela!")
        elif posicao == 1:
            embed.set_footer(text="Você está em primeiro lugar! 🏆")
        else:
            acima = sorted_members[posicao - 2]
            faltam = acima[1]["estrelas"] - total
            nome_acima = interaction.guild.get_member(int(acima[0]))
            nome_acima = nome_acima.display_name if nome_acima else acima[1]["nome"]
            embed.set_footer(text=f"Faltam {faltam} estrela(s) para superar {nome_acima}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ranking", description="Mostra o ranking de estrelas do servidor")
    async def ranking(self, interaction: discord.Interaction):
        data = _load()
        guild_data = data.get(str(interaction.guild_id), {})

        sorted_members = sorted(
            [(uid, info) for uid, info in guild_data.items() if info["estrelas"] > 0],
            key=lambda x: x[1]["estrelas"],
            reverse=True,
        )

        if not sorted_members:
            await interaction.response.send_message("Nenhuma estrela ativa no servidor.", ephemeral=True)
            return

        embed = discord.Embed(title="🏆 Ranking de Estrelas", color=discord.Color.gold())
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
