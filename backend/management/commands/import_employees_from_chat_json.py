import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from backend.models import Employee, Organization


class Command(BaseCommand):
    help = "Import employees from parsed Telegram chat JSON and attach them to all existing organizations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            required=True,
            help="Path to JSON produced by scripts/parse_admin_chat_html.py",
        )
        parser.add_argument(
            "--use-deduped",
            action="store_true",
            help="Use 'deduped_employees' section when present (dedupe by user_id).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be created/updated, without writing to DB.",
        )

    def handle(self, *args, **options):
        json_path = Path(options["path"])
        if not json_path.exists():
            raise CommandError(f"File not found: {json_path}")

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        employees_list = None
        if options["use_deduped"] and isinstance(payload, dict):
            employees_list = payload.get("deduped_employees")
        if employees_list is None and isinstance(payload, dict):
            employees_list = payload.get("employees")
        if not isinstance(employees_list, list):
            raise CommandError("Invalid JSON format: expected key 'employees' (or 'deduped_employees') to be a list.")

        orgs = list(Organization.objects.all())
        org_ids = [o.id for o in orgs]

        created = 0
        updated = 0
        attached = 0
        skipped = 0
        duplicates = 0

        def norm_int(x):
            try:
                return int(x)
            except Exception:
                return None

        with transaction.atomic():
            for rec in employees_list:
                if not isinstance(rec, dict):
                    skipped += 1
                    continue
                user_id = norm_int(rec.get("user_id"))
                name = (rec.get("name") or "").strip() or None
                if user_id is None:
                    skipped += 1
                    continue

                existing = list(Employee.objects.filter(user_id=user_id).order_by("id"))
                if not existing:
                    emp = Employee(user_id=user_id, name=name)
                    created += 1
                    emp.save()
                    existing = [emp]
                else:
                    if len(existing) > 1:
                        duplicates += (len(existing) - 1)

                for emp in existing:
                    # Only update name if empty and we have a value.
                    if name and (emp.name is None or str(emp.name).strip() == ""):
                        emp.name = name
                        updated += 1
                        emp.save(update_fields=["name"])

                    if orgs:
                        before = set(emp.organizations.values_list("id", flat=True))
                        missing = [oid for oid in org_ids if oid not in before]
                        if missing:
                            attached += len(missing)
                            emp.organizations.add(*missing)
                        if emp.active_organization_id is None:
                            emp.active_organization = orgs[0]
                            emp.save(update_fields=["active_organization"])

            if options["dry_run"]:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. created={created} updated={updated} attached={attached} skipped={skipped} duplicates={duplicates} orgs={len(orgs)}"
            )
        )

