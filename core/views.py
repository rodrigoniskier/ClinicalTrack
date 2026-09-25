from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q, Count
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


def visible_placements(user):
    role=current_role(user)
    qs=Placement.objects.select_related("trainee", "supervisor", "site", "period__area")
    if role == MemberProfile.Role.ADMIN: return qs
    if role == MemberProfile.Role.SUPERVISOR: return qs.filter(supervisor=user)
    if role == MemberProfile.Role.TRAINEE: return qs.filter(trainee=user)
    return qs.none()

@login_required
def dashboard(request):
    role=current_role(request.user)
    if not role: return HttpResponseForbidden("Perfil necessário.")
    placements=visible_placements(request.user)
    evaluations=Evaluation.objects.filter(placement__in=placements).select_related("placement__trainee", "placement__site")
    if role == MemberProfile.Role.TRAINEE: evaluations=evaluations.filter(shared_with_trainee=True)
    from django.db.models import Avg
    from .models import TrainingSite
    avg=evaluations.aggregate(k=Avg("knowledge"),s=Avg("skills"),p=Avg("professionalism"))
    score=round(sum(x or 0 for x in avg.values())/3,1)
    context={"mode":role.lower(),"placements":placements[:6],"evaluations":evaluations[:4],"notices":Notice.objects.filter(active=True).filter(Q(audience="ALL")|Q(audience=role))[:2],"stats":{"placements":placements.count(),"trainees":placements.values("trainee").distinct().count(),"evaluations":evaluations.count(),"score":score},"areas":list(placements.values("period__area__name").annotate(total=Count("id")))}
    return render(request,"dashboard.html",context)

@login_required
def placements_view(request):
    qs=visible_placements(request.user)
    q=request.GET.get("q","").strip()
    if q: qs=qs.filter(Q(trainee__first_name__icontains=q)|Q(trainee__last_name__icontains=q)|Q(site__name__icontains=q))
    return render(request,"placements.html",{"placements":qs,"mode":str(current_role(request.user)).lower()})

@role_required(MemberProfile.Role.ADMIN)
def program(request):
    from .models import RotationPeriod,TrainingSite,TrainingArea
    return render(request,"program.html",{"periods":RotationPeriod.objects.select_related("area"),"sites":TrainingSite.objects.all(),"areas":TrainingArea.objects.all()})

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
        from django.conf import settings
        if settings.PORTFOLIO_DEMO and Evaluation.objects.count() >= 150:
            return HttpResponseForbidden("Limite de registros da demonstração atingido.")
        evaluation.save()
        messages.success(request, "Avaliação registrada e disponível no acompanhamento.")
        return redirect("dashboard")
    return render(request, "evaluate.html", {"placement": placement, "form": form})


@require_POST
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")
