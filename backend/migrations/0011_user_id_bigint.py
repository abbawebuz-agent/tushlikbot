from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0010_alter_lead_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="user_id",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="cupon",
            name="user_id",
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]

