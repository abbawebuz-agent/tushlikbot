from aiogram.dispatcher.filters import BoundFilter

from data import config


class IsAdmin(BoundFilter):
    async def check(self, obj):
        # ADMIN_OPEN_TO_ALL=true бўлса, админ буйруқлари («11» коди, /admin, Add user,
        # рўйхатлар) БАРЧА фойдаланувчиларга очиқ бўлади.
        # Ёпиш учун: .env да ADMIN_OPEN_TO_ALL=false → poller'ни restart қилиш кифоя.
        if config.ADMIN_OPEN_TO_ALL:
            return True
        return obj.from_user.id in config.ADMINS
