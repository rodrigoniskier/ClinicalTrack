from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import EvaluationForm
from .models import Evaluation, MemberProfile, Notice, Placement


class ClinicalTrackLoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True


def current_role(user):
    if user.is_superuser:
        return MemberProfile.Role.ADMIN
    profile = getattr(user, "clinical_profile", None)
    return profile.role if profile else None


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if current_role(request.user) not in roles:
                return HttpResponseForbidden("You do not have access to this area.")
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


@login_required
def dashboard(request):
    role = current_role(request.user)
    notices = Notice.objects.filter(active=True).filter(Q(audience="ALL") | Q(audience=role))[:5]

    if role == MemberProfile.Role.ADMIN:
        placements = Placement.objects.select_related("trainee", "supervisor", "site", "period__area")[:50]
        return render(request, "dashboard.html", {"mode": "admin", "placements": placements, "notices": notices})

    if role == MemberProfile.Role.SUPERVISOR:
        placements = Placement.objects.filter(supervisor=request.user, active=True).select_related(
            "trainee", "site", "period__area"
        )
        evaluations = Evaluation.objects.filter(evaluator=request.user).select_related("placement__trainee")[:8]
        return render(request, "dashboard.html", {
            "mode": "supervisor", "placements": placements, "evaluations": evaluations, "notices": notices
        })

    if role == MemberProfile.Role.TRAINEE:
        placements = Placement.objects.filter(trainee=request.user).select_related(
            "supervisor", "site", "period__area"
        )
        evaluations = Evaluation.objects.filter(
            placement__trainee=request.user, shared_with_trainee=True
        ).select_related("placement__supervisor", "placement__site")
        return render(request, "dashboard.html", {
            "mode": "trainee", "placements": placements, "evaluations": evaluations, "notices": notices
        })

    return HttpResponseForbidden("A ClinicalTrack role is required.")


@role_required(MemberProfile.Role.SUPERVISOR)
def evaluate(request, placement_id):
    placement = get_object_or_404(
        Placement.objects.select_related("trainee", "site", "period__area"),
        id=placement_id,
        supervisor=request.user,
        active=True,
    )
    form = EvaluationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        evaluation = form.save(commit=False)
        evaluation.placement = placement
        evaluation.evaluator = request.user
        evaluation.full_clean()
        evaluation.save()
        messages.success(request, "Evaluation recorded.")
        return redirect("dashboard")
    return render(request, "evaluate.html", {"placement": placement, "form": form})


@require_POST
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")
