# bot/views.py
import json

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from data import config
from handlers import dp

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

    async_to_sync(dp.process_update)(update)

    return JsonResponse({"status": "ok"})
