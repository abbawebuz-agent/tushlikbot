# bot/views.py
import json
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from data import config
from handlers import dp
from .forms import LeadForm

logger = logging.getLogger(__name__)


@csrf_exempt
def webhook(request, secret: str):
    if secret != config.WEBHOOK_SECRET:
        return JsonResponse({"status": "not found"}, status=404)

    if request.method != "POST":
        return JsonResponse({"status": "invalid request"}, status=400)

    json_str = request.body.decode("utf-8")
    json_data = json.loads(json_str)
    update = Update.to_object(json_data)

    Bot.set_current(dp.bot)
    Dispatcher.set_current(dp)

    chat_id = getattr(getattr(update.message, "chat", None), "id", None) if update.message else None
    user_id = getattr(getattr(update.message, "from_user", None), "id", None) if update.message else None
    text = getattr(update.message, "text", None) if update.message else None

    fsm_state = None
    if chat_id is not None and user_id is not None:
        try:
            ctx = dp.current_state(chat=chat_id, user=user_id)
            fsm_state = async_to_sync(ctx.get_state)()
        except Exception:
            logger.exception("failed to read fsm_state in webhook")
    logger.info(
        "telegram webhook pid=%s update_id=%s chat_id=%s user_id=%s text=%r fsm_state=%s",
        os.getpid(),
        update.update_id,
        chat_id,
        user_id,
        text,
        fsm_state,
    )

    try:
        async_to_sync(dp.process_update)(update)
    except Exception:
        logger.exception("dp.process_update failed")

    return JsonResponse({"status": "ok"})


@require_http_methods(["GET", "POST"])
def landing(request):
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/?sent=1")
    else:
        form = LeadForm()

    sent = request.GET.get("sent") == "1"
    return render(request, "landing/index.html", {"form": form, "sent": sent})
