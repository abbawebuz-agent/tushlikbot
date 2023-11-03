from datetime import date, datetime
from typing import List, Any
from asgiref.sync import sync_to_async
from backend.admin import Employee
from backend.models import *


@sync_to_async
def get_employee(user_id):
    try:
        user = Employee.objects.filter(user_id=user_id).first()
        return user
    except:
        return None


@sync_to_async
def add_employee(user_id, full_name):
    try:
        emp = Employee.objects.create(user_id=user_id, name=full_name).save()
        return emp
    except Exception as exx:
        print(exx)
        return None


@sync_to_async
def add_coupon(user_id):
    user = Employee.objects.filter(user_id=user_id).first()
    try:
        today = date.today()
        tickets = Cupon.objects.filter(user_id=user_id, date=today).all()
        if tickets:
            return None
        else:
            ticket = Cupon.objects.create(user_id=user_id, name=user.name)
            ticket.save()
            return ticket.id
    except Exception as exx:
        print(exx)
        return None

    
@sync_to_async
def list_today() -> List[Cupon]:
    today = date.today()
    eps = Cupon.objects.filter(date=today).all()
    return eps
    
    
@sync_to_async
def get_employees() -> List[Employee]:
    eps = Employee.objects.all()
    return eps
    
    
@sync_to_async
def get_cupon_count(user_id):
    today = date.today()
    
    cps = Cupon.objects.filter(user_id=user_id, date=today).all()
    return len(cps)

 
@sync_to_async
def list_this_month()-> List[Cupon]:
    month = date.today().month
    year = date.today().year
    cps = []
    eps = Cupon.objects.all()
    for i in eps:
        if i.date.month == month and i.date.year == year:
            cps.append(i)
    return cps


@sync_to_async
def get_cupons()-> List[Cupon]:
    eps = Cupon.objects.all()
    return eps


@sync_to_async
def not_checked(id):
    try:
        a = []
        cupons = Cupon.objects.filter(checked=False).all()
        for i in cupons:
            if i.id <= id:
                a.append(i)
        return a
    except:
        return None


@sync_to_async
def check_count(id):
    try:
        a = 0
        cupons = Cupon.objects.filter(checked=False).all()
        for i in cupons:
            if id is not None and i.id <= id:
                a += 1
        return a
    except:
        return None

    