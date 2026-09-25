from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class MemberProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        SUPERVISOR = "SUPERVISOR", "Supervisor"
        TRAINEE = "TRAINEE", "Trainee"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="clinical_profile")
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.TRAINEE)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} · {self.get_role_display()}"


class TrainingArea(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class TrainingSite(models.Model):
    name = models.CharField(max_length=140, unique=True)
    city = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class RotationPeriod(models.Model):
    area = models.ForeignKey(TrainingArea, on_delete=models.PROTECT, related_name="periods")
    starts_on = models.DateField()
    ends_on = models.DateField()
    label = models.CharField(max_length=120, blank=True)

    def clean(self):
        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValidationError({"ends_on": "End date cannot be before start date."})

    def __str__(self):
        return self.label or f"{self.area} · {self.starts_on}–{self.ends_on}"


class Placement(models.Model):
    trainee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="training_placements")
    supervisor = models.ForeignKey(User, on_delete=models.PROTECT, related_name="supervised_placements")
    site = models.ForeignKey(TrainingSite, on_delete=models.PROTECT, related_name="placements")
    period = models.ForeignKey(RotationPeriod, on_delete=models.PROTECT, related_name="placements")
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("trainee", "site", "period"), name="unique_trainee_site_period")
        ]

    def clean(self):
        if self.trainee_id:
            role = getattr(getattr(self.trainee, "clinical_profile", None), "role", None)
            if role != MemberProfile.Role.TRAINEE:
                raise ValidationError({"trainee": "Selected user must be a trainee."})
        if self.supervisor_id:
            role = getattr(getattr(self.supervisor, "clinical_profile", None), "role", None)
            if role != MemberProfile.Role.SUPERVISOR:
                raise ValidationError({"supervisor": "Selected user must be a supervisor."})

    def __str__(self):
        return f"{self.trainee} · {self.site} · {self.period}"


class Evaluation(models.Model):
    placement = models.ForeignKey(Placement, on_delete=models.CASCADE, related_name="evaluations")
    evaluator = models.ForeignKey(User, on_delete=models.PROTECT, related_name="training_evaluations")
    knowledge = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    skills = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    professionalism = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField(blank=True)
    shared_with_trainee = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    @property
    def average(self):
        return round((self.knowledge + self.skills + self.professionalism) / 3, 2)

    def clean(self):
        if self.placement_id and self.evaluator_id != self.placement.supervisor_id:
            raise ValidationError({"evaluator": "Only the assigned supervisor may evaluate this placement."})


class Notice(models.Model):
    title = models.CharField(max_length=160)
    body = models.TextField()
    audience = models.CharField(
        max_length=16,
        choices=[("ALL", "Everyone"), ("SUPERVISOR", "Supervisors"), ("TRAINEE", "Trainees")],
        default="ALL",
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
