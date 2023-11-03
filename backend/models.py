from django.db import models


class Employee(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    user_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    

class Cupon(models.Model):
    user_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateField(auto_now_add=True, null=True)
    checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} {self.date}"

    
