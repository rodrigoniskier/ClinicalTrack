from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="MemberProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("role", models.CharField(choices=[("ADMIN","Administrator"),("SUPERVISOR","Supervisor"),("TRAINEE","Trainee")], default="TRAINEE", max_length=16)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="clinical_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="TrainingArea",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="TrainingSite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=140, unique=True)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("active", models.BooleanField(default=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Notice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=160)),
                ("body", models.TextField()),
                ("audience", models.CharField(choices=[("ALL","Everyone"),("SUPERVISOR","Supervisors"),("TRAINEE","Trainees")], default="ALL", max_length=16)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="RotationPeriod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("starts_on", models.DateField()),
                ("ends_on", models.DateField()),
                ("label", models.CharField(blank=True, max_length=120)),
                ("area", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="periods", to="core.trainingarea")),
            ],
        ),
        migrations.CreateModel(
            name="Placement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("active", models.BooleanField(default=True)),
                ("period", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="placements", to="core.rotationperiod")),
                ("site", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="placements", to="core.trainingsite")),
                ("supervisor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="supervised_placements", to=settings.AUTH_USER_MODEL)),
                ("trainee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="training_placements", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name="placement",
            constraint=models.UniqueConstraint(fields=("trainee","site","period"), name="unique_trainee_site_period"),
        ),
        migrations.CreateModel(
            name="Evaluation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("knowledge", models.PositiveSmallIntegerField()),
                ("skills", models.PositiveSmallIntegerField()),
                ("professionalism", models.PositiveSmallIntegerField()),
                ("feedback", models.TextField(blank=True)),
                ("shared_with_trainee", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("evaluator", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="training_evaluations", to=settings.AUTH_USER_MODEL)),
                ("placement", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="evaluations", to="core.placement")),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
