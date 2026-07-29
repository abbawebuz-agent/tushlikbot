from aiogram.dispatcher.filters import BoundFilter

from data import config


class IsAdmin(BoundFilter):
    async def check(self, obj):
        return obj.from_user.id in config.ADMINS
