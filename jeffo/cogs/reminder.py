from __future__ import annotations
import asyncio
from discord import TextChannel
from discord.ext import tasks
from discord.ext.commands import Bot, Cog, command, Context, has_permissions
from jeffo.utils.constants import _CharList
from jeffo.utils.time import DatetimeGenerator
from jeffo.models.state import State, StateManager
from typing import List
import datetime


class Reminder(Cog):
    times = DatetimeGenerator.generate_range()

    def __init__(self, bot: Bot) -> None:
        self.client = bot
        self.state_manager = StateManager(self.client, State.JEFFO)

    @tasks.loop(time=times)
    async def bot_update(self, channel: TextChannel) -> None:
        await self.state_manager.set_state()
        await asyncio.sleep(1800)

    @command(name="start")
    @has_permissions(administrator=True)
    async def start(self, ctx: Context) -> None:
        await ctx.send("Started!")
        self.bot_update.start(ctx.channel)


async def setup(bot):
    await bot.add_cog(Reminder(bot))
