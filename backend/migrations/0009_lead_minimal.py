from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0008_lead"),
    ]

    operations = [
        migrations.RemoveField(name="company", model_name="lead"),
        migrations.RemoveField(name="email", model_name="lead"),
        migrations.RemoveField(name="message", model_name="lead"),
        migrations.AlterField(model_name="lead", name="contact_name", field=models.CharField(max_length=200)),
        migrations.AlterField(model_name="lead", name="phone", field=models.CharField(max_length=64)),
    ]

