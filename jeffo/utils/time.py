from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import app_commands
from typing import List
import re

if TYPE_CHECKING:
    from typing_extensions import Self


class DatetimeGenerator:

    @staticmethod
    def generate_range() -> List[datetime.time]:
        times = []
        for i in range(24):
            times.append(datetime.time(hour=i, minute=30))
        return times
