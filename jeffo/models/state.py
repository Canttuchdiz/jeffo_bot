from discord import Color
from discord.ext.commands import Bot
from discord.types.snowflake import Snowflake
from jeffo.utils.constants import _CharList
from jeffo.utils.config import Config
from enum import Enum
import string


class State(Enum):
    JEFFO = 0
    GOLDEN = 1
    CHICK = 2
    CHIMKEN = 3
    GRAM = 4
    BEANS = 5


class StateManager:
    def __init__(self, bot: Bot, state: State) -> None:
        self.client = bot
        self.state = state

    async def set_state(self) -> None:
        await self._change_state()
        await self._apply_state()

    async def _change_state(self) -> State:
        index = self.state.value
        if index == len(_CharList.characters) - 1:
            index = 0
        else:
            index += 1
        state = State(index)
        self.state = state
        return state

    async def _apply_state(self) -> string:
        role = self.client.get_guild(Config.GUILD_ID).get_role(Config.ROLE_ID)
        character = _CharList.characters[self.state.value]
        username = string.capwords(character.replace('_', ' '))
        avatarUrl = 'assets/' + character + '.png'
        with open(avatarUrl, 'rb') as image:
            await self.client.user.edit(username=username, avatar=image.read())
        rgb = _CharList.colors[self.state.value]
        await role.edit(color=Color.from_rgb(rgb[0], rgb[1], rgb[2]))
        return username
