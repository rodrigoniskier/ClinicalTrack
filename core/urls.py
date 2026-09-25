from django.urls import path
from .views import ClinicalTrackLoginView, dashboard, evaluate, logout_view

urlpatterns = [
    path("login/", ClinicalTrackLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("", dashboard, name="dashboard"),
    path("placements/<int:placement_id>/evaluate/", evaluate, name="evaluate"),
]

from .views import placements_view, program
urlpatterns += [path("placements/",placements_view,name="placements"),path("program/",program,name="program")]
