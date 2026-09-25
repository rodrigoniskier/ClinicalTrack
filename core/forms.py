from django import forms
from .models import Evaluation

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ["knowledge", "skills", "professionalism", "feedback", "shared_with_trainee"]
        labels = {"knowledge":"Conhecimento", "skills":"Habilidades", "professionalism":"Profissionalismo", "feedback":"Feedback e próximos passos", "shared_with_trainee":"Compartilhar com o trainee"}
        widgets = {
            "knowledge": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "skills": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "professionalism": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "feedback": forms.Textarea(attrs={"rows": 4}),
        }
