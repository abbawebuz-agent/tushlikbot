import logging
from datetime import date
from typing import List, Optional

from asgiref.sync import sync_to_async

from backend.models import Employee, Cupon, Organization

logger = logging.getLogger(__name__)


@sync_to_async
def get_organization_by_start_code(start_code: str) -> Optional[Organization]:
    try:
        return Organization.objects.filter(start_code=start_code).first()
    except Exception:
        return None


@sync_to_async
def get_default_organization() -> Optional[Organization]:
    try:
        return Organization.objects.filter(is_default=True).first() or Organization.objects.first()
    except Exception:
        return None


@sync_to_async
def get_all_organizations() -> List[Organization]:
    return list(Organization.objects.order_by("name", "id").all())


@sync_to_async
def get_employee(user_id, organization_id: Optional[int] = None):
    try:
        qs = Employee.objects.filter(user_id=user_id)
        if organization_id is not None:
            qs = qs.filter(organizations__id=organization_id)
        return qs.distinct().first()
    except:
        return None


@sync_to_async
def ensure_employee_stub(user_id: int, organization_id: Optional[int] = None):
    """
    По Telegram user_id: найти сотрудника или создать без ФИО (name пустой),
    привязать к организациям как при регистрации нового.
    """
    try:
        logger.info("[DB:ensure_employee_stub] called %s", {"user_id": user_id, "organization_id": organization_id})
        emp = Employee.objects.filter(user_id=user_id).first()
        if emp is not None:
            logger.info(
                "[DB:ensure_employee_stub] existing %s",
                {"id": emp.id, "user_id": emp.user_id, "name": emp.name},
            )
            if organization_id is not None:
                emp.organizations.add(organization_id)
                if emp.active_organization_id is None:
                    emp.active_organization_id = organization_id
                    emp.save(update_fields=["active_organization"])
            return emp

        emp = Employee.objects.create(user_id=user_id, name=None)
        logger.info("[DB:ensure_employee_stub] created stub %s", {"id": emp.id, "user_id": emp.user_id})
        org_ids = list(Organization.objects.values_list("id", flat=True))
        if org_ids:
            emp.organizations.add(*org_ids)
        if organization_id is not None:
            emp.organizations.add(organization_id)
            emp.active_organization_id = organization_id
            emp.save(update_fields=["active_organization"])
            logger.info(
                "[DB:ensure_employee_stub] set active organization %s",
                {"employee_id": emp.id, "organization_id": organization_id},
            )
        return emp
    except Exception:
        logger.exception("[DB:ensure_employee_stub] failed")
        return None


@sync_to_async
def set_employee_name(user_id: int, full_name: str):
    try:
        logger.info("[DB:set_employee_name] called %s", {"user_id": user_id, "full_name": full_name})
        emp = Employee.objects.filter(user_id=user_id).first()
        if emp is None:
            logger.warning("[DB:set_employee_name] employee not found user_id=%s", user_id)
            return None
        name = (full_name or "").strip() or None
        emp.name = name
        emp.save(update_fields=["name"])
        logger.info("[DB:set_employee_name] updated %s", {"id": emp.id, "name": emp.name})
        return emp
    except Exception:
        logger.exception("[DB:set_employee_name] failed")
        return None


@sync_to_async
def set_employee_active_organization(user_id: int, organization_id: Optional[int]):
    try:
        if organization_id is None:
            return None
        emp = Employee.objects.filter(user_id=user_id).first()
        if emp is None:
            return None
        emp.organizations.add(organization_id)
        emp.active_organization_id = organization_id
        emp.save(update_fields=["active_organization"])
        return emp
    except Exception:
        return None


@sync_to_async
def add_coupon(user_id, organization_id: Optional[int] = None):
    if organization_id is not None:
        user = Employee.objects.filter(user_id=user_id, organizations__id=organization_id).distinct().first()
    else:
        user = Employee.objects.filter(user_id=user_id).first()
    try:
        today = date.today()
        if organization_id is not None:
            tickets = Cupon.objects.filter(user_id=user_id, organization_id=organization_id, date=today).all()
        else:
            tickets = Cupon.objects.filter(user_id=user_id, date=today).all()
        if tickets:
            return None
        else:
            if organization_id is not None:
                ticket = Cupon.objects.create(
                    user_id=user_id,
                    name=user.name,
                    organization_id=organization_id,
                )
            else:
                ticket = Cupon.objects.create(user_id=user_id, name=user.name)
            return ticket.id
    except Exception as exx:
        print(exx)
        return None

    
@sync_to_async
def list_today(organization_id: Optional[int] = None) -> List[Cupon]:
    today = date.today()
    qs = Cupon.objects.filter(date=today)
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    return list(qs)
    
    
@sync_to_async
def get_employees(organization_id: Optional[int] = None) -> List[Employee]:
    qs = Employee.objects.all()
    if organization_id is not None:
        qs = qs.filter(organizations__id=organization_id)
    return list(qs.distinct())
    
    
@sync_to_async
def get_cupon_count(user_id, organization_id: Optional[int] = None):
    today = date.today()

    qs = Cupon.objects.filter(user_id=user_id, date=today)
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    return len(qs.all())

 
@sync_to_async
def list_this_month(organization_id: Optional[int] = None) -> List[Cupon]:
    month = date.today().month
    year = date.today().year
    cps = []
    eps = Cupon.objects.all()
    if organization_id is not None:
        eps = eps.filter(organization_id=organization_id)
    for i in eps:
        if i.date.month == month and i.date.year == year:
            cps.append(i)
    return cps


@sync_to_async
def get_cupons(organization_id: Optional[int] = None) -> List[Cupon]:
    qs = Cupon.objects.all()
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    return list(qs)


@sync_to_async
def not_checked(id, organization_id: Optional[int] = None):
    try:
        qs = Cupon.objects.filter(checked=False)
        if organization_id is not None:
            qs = qs.filter(organization_id=organization_id)
        if id is not None:
            qs = qs.filter(id__lte=id)
        return list(qs)
    except:
        return None


@sync_to_async
def mark_cupons_checked(cupon_ids: List[int]) -> None:
    if not cupon_ids:
        return
    Cupon.objects.filter(id__in=cupon_ids).update(checked=True)


@sync_to_async
def check_count(id, organization_id: Optional[int] = None):
    try:
        if id is None:
            return 0
        qs = Cupon.objects.filter(checked=False, id__lte=id)
        if organization_id is not None:
            qs = qs.filter(organization_id=organization_id)
        return qs.count()
    except:
        return None

    