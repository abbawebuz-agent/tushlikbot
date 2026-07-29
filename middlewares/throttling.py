import asyncio
import logging
import os

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    # noinspection PyUnusedLocal
    async def on_process_message(self, message: types.Message, data: dict):
        # Пока хендлер ещё не выбран, старый код использовал один ключ `*_message`
        # на все сообщения чата → второе сообщение (например user_id после «Add user»)
        # часто получало Throttled/CancelHandler и обработчик даже не вызывался (нет логов).
        if message.from_user is not None:
            dispatcher = Dispatcher.get_current()
            try:
                state = dispatcher.current_state(
                    chat=message.chat.id,
                    user=message.from_user.id,
                )
                current = await state.get_state()
                logger.info(
                    "[Throttling] pid=%s chat_id=%s user_id=%s text=%r fsm_state=%s",
                    os.getpid(),
                    message.chat.id,
                    message.from_user.id,
                    message.text,
                    current,
                )
                if current:
                    return
            except Exception:
                logger.exception("[Throttling] failed to read fsm_state")

        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            # В этом проекте многие хендлеры буквально называются `handler`
            # (одинаковое имя функции), поэтому ключ по handler.__name__
            # склеивал их все в один общий лимит. id(handler) уникален
            # для каждой конкретной функции-обработчика.
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{id(handler)}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message_{message.chat.id}"
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            logger.warning(
                "[Throttling] pid=%s throttled key=%s chat_id=%s user_id=%s text=%r",
                os.getpid(),
                key,
                message.chat.id,
                getattr(message.from_user, "id", None),
                message.text,
            )
            await self.message_throttled(message, t)
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{id(handler)}")
        else:
            key = f"{self.prefix}_message_{message.chat.id}"
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count <= 2:
            await message.reply('Too many requests! ')
        await asyncio.sleep(delta)
        thr = await dispatcher.check_key(key)
        if thr.exceeded_count == throttled.exceeded_count:
            await message.reply('Unlocked.')
