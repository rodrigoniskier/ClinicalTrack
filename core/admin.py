from django.contrib import admin
from .models import Evaluation, MemberProfile, Notice, Placement, RotationPeriod, TrainingArea, TrainingSite

admin.site.register(MemberProfile)
admin.site.register(TrainingArea)
admin.site.register(TrainingSite)
admin.site.register(RotationPeriod)
admin.site.register(Placement)
admin.site.register(Evaluation)
admin.site.register(Notice)
admin.site.site_header = "ClinicalTrack Administration"
admin.site.site_title = "ClinicalTrack"
