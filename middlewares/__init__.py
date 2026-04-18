from aiogram import Dispatcher

from .throttling import ThrottlingMiddleware


def setup(dp: Dispatcher):
    # Django webhook + polling both вызывают setup — не дублировать middleware.
    if getattr(dp, "_throttling_middleware_installed", False):
        return
    dp.middleware.setup(ThrottlingMiddleware())
    dp._throttling_middleware_installed = True
