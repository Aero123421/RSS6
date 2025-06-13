import logging
from typing import Dict, Any

import discord
from discord import app_commands
from discord.ext import commands

from ..ui_components import ConfigView, FeedListView

logger = logging.getLogger(__name__)


class RSSCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.feed_manager = getattr(bot, "feed_manager")
        self.config_manager = getattr(bot, "config_manager")
        self.config: Dict[str, Any] = (
            self.config_manager.get_config() if self.config_manager else {}
        )

    rss = app_commands.Group(name="rss", description="RSSフィード関連のコマンド")

    @rss.command(name="config", description="設定パネルを表示します")
    @app_commands.checks.has_permissions(administrator=True)
    async def rss_config(self, interaction: discord.Interaction):
        admin_ids = self.config.get("admin_ids", [])
        if admin_ids and str(interaction.user.id) not in admin_ids:
            await interaction.response.send_message(
                "このコマンドを実行する権限がありません。サーバー管理者に連絡してください。",
                ephemeral=True,
            )
            return
        embed = discord.Embed(
            title="RSS Bot 設定パネル",
            description="以下のオプションから設定を変更できます。",
            color=discord.Color(self.config.get("embed_color", 3447003)),
        )
        embed.add_field(
            name="現在の設定",
            value=(
                f"AIモデル: {self.config.get('ai_model','gemini-2.0-flash')}\n"
                f"確認間隔: {self.config.get('check_interval',15)}分\n"
                f"要約: {'有効' if self.config.get('summarize',True) else '無効'}\n"
                f"ジャンル分類: {'有効' if self.config.get('classify',False) else '無効'}\n"
                f"サムネイル: {'有効' if self.config.get('use_thumbnails',True) else '無効'}"
            ),
            inline=False,
        )
        view = ConfigView(
            self.config, self.config_manager, self.feed_manager, interaction.guild
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @rss.command(
        name="list_feeds", description="登録されているフィードの一覧を表示します"
    )
    async def list_feeds(self, interaction: discord.Interaction):
        feeds = self.feed_manager.get_feeds()
        if not feeds:
            await interaction.response.send_message(
                "登録されているフィードはありません。", ephemeral=True
            )
            return
        embed = discord.Embed(
            title="登録フィード一覧",
            description=f"登録されているフィード: {len(feeds)}件",
            color=discord.Color(self.config.get("embed_color", 3447003)),
        )
        view = FeedListView(feeds, self.config, self.config_manager, self.feed_manager)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @rss.command(name="status", description="ボットのステータスを表示します")
    async def status(self, interaction: discord.Interaction):
        feeds_count = len(self.feed_manager.get_feeds())
        checking = self.feed_manager.checking
        embed = discord.Embed(
            title="RSS Bot ステータス",
            color=discord.Color(self.config.get("embed_color", 3447003)),
        )
        embed.add_field(name="登録フィード数", value=str(feeds_count), inline=True)
        embed.add_field(
            name="確認間隔",
            value=f"{self.config.get('check_interval',15)}分",
            inline=True,
        )
        embed.add_field(
            name="フィード確認中", value="はい" if checking else "いいえ", inline=True
        )
        embed.add_field(
            name="AIモデル",
            value=self.config.get("ai_model", "gemini-2.0-flash"),
            inline=True,
        )
        embed.add_field(
            name="要約",
            value="有効" if self.config.get("summarize", True) else "無効",
            inline=True,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RSSCog(bot))
