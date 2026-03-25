from django.db import models


class Organization(models.Model):
    """
    Мультиорганизационность в рамках одного деплоя бота.
    QR-код (payload в /start) должен указывать `start_code` этой организации.
    """

    name = models.CharField(max_length=200, blank=True, null=True)
    start_code = models.CharField(max_length=120, unique=True)

    # Telegram chat/channel ids (negative ids for groups/channels)
    channel_id = models.BigIntegerField()
    uzoman_channel_id = models.BigIntegerField(null=True, blank=True)

    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.start_code


class Employee(models.Model):
    organizations = models.ManyToManyField(
        Organization,
        blank=True,
        related_name="employees",
    )
    active_organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="active_employees",
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    user_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name or str(self.user_id)
    

class Cupon(models.Model):
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="cupons",
    )
    user_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateField(auto_now_add=True, null=True)
    checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} {self.date}"

    
