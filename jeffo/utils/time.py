from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, Optional, Union
from dateutil.relativedelta import relativedelta
from .formats import plural, human_join, format_dt as format_dt
from discord.ext import commands
from discord import app_commands
from typing import List
import re

if TYPE_CHECKING:
    from typing_extensions import Self


class ShortTime:
    compiled = re.compile(
        """
           (?:(?P<years>[0-9])(?:years?|y))?                    # e.g. 2y
           (?:(?P<months>[0-9]{1,2})(?:months?|mon?))?          # e.g. 2months
           (?:(?P<weeks>[0-9]{1,4})(?:weeks?|w))?               # e.g. 10w
           (?:(?P<days>[0-9]{1,5})(?:days?|d))?                 # e.g. 14d
           (?:(?P<hours>[0-9]{1,5})(?:hours?|hr?))?             # e.g. 12h
           (?:(?P<minutes>[0-9]{1,5})(?:minutes?|m(?:in)?))?    # e.g. 10m
           (?:(?P<seconds>[0-9]{1,5})(?:seconds?|s(?:ec)?))?    # e.g. 15s
        """,
        re.VERBOSE,
    )

    discord_fmt = re.compile(r'<t:(?P<ts>[0-9]+)(?:\:?[RFfDdTt])?>')

    dt: datetime.datetime

    def __init__(self, argument: str, *, now: Optional[datetime.datetime] = None):
        match = self.compiled.fullmatch(argument)
        if match is None or not match.group(0):
            match = self.discord_fmt.fullmatch(argument)
            if match is not None:
                self.dt = datetime.datetime.fromtimestamp(int(match.group('ts')), tz=datetime.timezone.utc)
                return
            else:
                raise commands.BadArgument('invalid time provided')

        data = {k: int(v) for k, v in match.groupdict(default=0).items()}
        now = now or datetime.datetime.now(datetime.timezone.utc)
        self.dt = now + relativedelta(**data)

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> Self:
        return cls(argument, now=ctx.message.created_at)


class BadTimeTransform(app_commands.AppCommandError):
    pass


def human_timedelta(
        dt: datetime.datetime,
        *,
        source: Optional[datetime.datetime] = None,
        accuracy: Optional[int] = 3,
        brief: bool = False,
        suffix: bool = True,
) -> str:
    now = source or datetime.datetime.now(datetime.timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    if now.tzinfo is None:
        now = now.replace(tzinfo=datetime.timezone.utc)

    # Microsecond free zone
    now = now.replace(microsecond=0)
    dt = dt.replace(microsecond=0)

    # This implementation uses relativedelta instead of the much more obvious
    # divmod approach with seconds because the seconds approach is not entirely
    # accurate once you go over 1 week in terms of accuracy since you have to
    # hardcode a month as 30 or 31 days.
    # A query like "11 months" can be interpreted as "!1 months and 6 days"
    if dt > now:
        delta = relativedelta(dt, now)
        output_suffix = ''
    else:
        delta = relativedelta(now, dt)
        output_suffix = ' ago' if suffix else ''

    attrs = [
        ('year', 'y'),
        ('month', 'mo'),
        ('day', 'd'),
        ('hour', 'h'),
        ('minute', 'm'),
        ('second', 's'),
    ]

    output = []
    for attr, brief_attr in attrs:
        elem = getattr(delta, attr + 's')
        if not elem:
            continue

        if attr == 'day':
            weeks = delta.weeks
            if weeks:
                elem -= weeks * 7
                if not brief:
                    output.append(format(plural(weeks), 'week'))
                else:
                    output.append(f'{weeks}w')

        if elem <= 0:
            continue

        if brief:
            output.append(f'{elem}{brief_attr}')
        else:
            output.append(format(plural(elem), attr))

    if accuracy is not None:
        output = output[:accuracy]

    if len(output) == 0:
        return 'now'
    else:
        if not brief:
            return human_join(output, final='and') + output_suffix
        else:
            return ' '.join(output) + output_suffix


def format_relative(dt: datetime.datetime) -> str:
    return format_dt(dt, 'R')


class DatetimeGenerator:

    @staticmethod
    def generate_range() -> List[datetime.time]:
        times = []
        for i in range(24):
            times.append(datetime.time(hour=i, minute=30))
        return times
