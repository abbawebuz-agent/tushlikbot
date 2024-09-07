# bot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from asgiref.sync import async_to_sync

import asyncio
import json
from handlers import dp

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        json_str = request.body.decode('UTF-8')
        json_data = json.loads(json_str)
        update = Update.to_object(json_data)

        # Set the current bot and dispatcher instances
        Bot.set_current(dp.bot)
        Dispatcher.set_current(dp)

        # Ensure an active event loop is available
        try:
            # Try to get the existing running event loop
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            print(str(e), "%$%%%%%%")
            # Create a new event loop if none is running
            if "no current event loop" in str(e):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

        # Run the async function within the loop
        loop.run_until_complete(dp.process_update(update))

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'invalid request'}, status=400)
