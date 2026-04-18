from django.apps import AppConfig


class BackendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend"

    def ready(self):
        # Webhook (Gunicorn): подключить те же middleware/filters, что и в run.py (polling).
        import filters
        import middlewares
        from handlers import dp

        filters.setup(dp)
        middlewares.setup(dp)
