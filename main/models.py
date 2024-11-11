from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Person(models.Model):
    person = models.OneToOneField(User, on_delete=models.CASCADE)
    is_manger = models.BooleanField(default=False)
    is_player = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.person.username

class BankBook(models.Model):
    user = models.OneToOneField(Person, on_delete=models.CASCADE)
    balance_won = models.IntegerField(default = 0)
    balance_dol = models.IntegerField(default = 0)
    balance_yen = models.IntegerField(default = 0)
    balance_pes = models.IntegerField(default = 0)

    def __str__(self) -> str:
        return self.user.person.username

class Exchange(models.Model):
    dollar2won = models.IntegerField(default = 0)
    yenn2won = models.IntegerField(default = 0)
    pesso2won = models.IntegerField(default = 0)

    def __str__(self) -> str:
        return f"{self.dollar2won}won/dol, {self.yenn2won}won/yen, {self.pesso2won}won/yen"
    
class Log(models.Model):
    username = models.CharField(max_length= 100)
    currency = models.CharField(max_length= 100)
    change = models.IntegerField(default = 0)
    from django.utils import timezone
    reg_time = models.DateTimeField(default=timezone.now)  