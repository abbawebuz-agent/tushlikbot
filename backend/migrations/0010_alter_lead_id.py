from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0009_lead_minimal"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lead",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
    ]

