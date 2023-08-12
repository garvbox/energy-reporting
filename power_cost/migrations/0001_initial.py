# Generated by Django 4.2.1 on 2023-08-10 22:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Rate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("rate", models.DecimalField(decimal_places=2, max_digits=8)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "group",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="auth.group"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RatePeriod",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("start_hour", models.IntegerField()),
                ("end_hour", models.IntegerField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "rate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="power_cost.rate"
                    ),
                ),
            ],
        ),
    ]
