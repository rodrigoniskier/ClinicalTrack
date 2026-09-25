from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Evaluation, MemberProfile, Placement, RotationPeriod, TrainingArea, TrainingSite


class AuthorizationTests(TestCase):
    def setUp(self):
        area = TrainingArea.objects.create(name="Practice")
        site = TrainingSite.objects.create(name="Demo Site")
        period = RotationPeriod.objects.create(area=area, starts_on="2026-01-01", ends_on="2026-01-31")
        self.sup = User.objects.create_user("sup", password="long-password-123")
        self.other = User.objects.create_user("other", password="long-password-123")
        self.trainee = User.objects.create_user("trainee", password="long-password-123")
        MemberProfile.objects.create(user=self.sup, role=MemberProfile.Role.SUPERVISOR)
        MemberProfile.objects.create(user=self.other, role=MemberProfile.Role.SUPERVISOR)
        MemberProfile.objects.create(user=self.trainee, role=MemberProfile.Role.TRAINEE)
        self.placement = Placement.objects.create(
            trainee=self.trainee, supervisor=self.sup, site=site, period=period
        )

    def test_other_supervisor_cannot_evaluate(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("evaluate", args=[self.placement.id]))
        self.assertEqual(response.status_code, 404)

    def test_trainee_sees_only_shared_feedback(self):
        Evaluation.objects.create(
            placement=self.placement, evaluator=self.sup, knowledge=5, skills=5,
            professionalism=5, feedback="private-feedback", shared_with_trainee=False
        )
        Evaluation.objects.create(
            placement=self.placement, evaluator=self.sup, knowledge=4, skills=4,
            professionalism=4, feedback="shared-feedback", shared_with_trainee=True
        )
        self.client.force_login(self.trainee)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "shared-feedback")
        self.assertNotContains(response, "private-feedback")
