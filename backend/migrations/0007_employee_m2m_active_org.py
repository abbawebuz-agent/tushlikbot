from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0006_organization_multitenancy"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="active_organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="active_employees",
                to="backend.organization",
            ),
        ),
        migrations.AddField(
            model_name="employee",
            name="organizations",
            field=models.ManyToManyField(
                blank=True,
                related_name="employees",
                to="backend.organization",
            ),
        ),
        migrations.RemoveField(
            model_name="employee",
            name="organization",
        ),
    ]

