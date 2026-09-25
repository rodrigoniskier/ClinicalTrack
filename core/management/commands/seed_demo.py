from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import MemberProfile, TrainingArea, TrainingSite, RotationPeriod, Placement, Evaluation, Notice

class Command(BaseCommand):
    help = 'Seed an isolated portfolio database with synthetic training records (idempotent).'
    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.PORTFOLIO_DEMO:
            raise CommandError('Set PORTFOLIO_DEMO=1 on a dedicated demo database.')
        def member(username, name, role):
            first,last=name.split(' ',1)
            user,_=User.objects.get_or_create(username=username,defaults={'first_name':first,'last_name':last,'email':username+'@example.invalid'})
            user.is_staff=False; user.is_superuser=False; user.set_unusable_password(); user.save()
            MemberProfile.objects.update_or_create(user=user,defaults={'role':role})
            return user
        member('manager.demo','Beatriz Andrade','ADMIN')
        supervisors=[member('supervisor.demo' if i==0 else f'supervisor.{i}',name,'SUPERVISOR') for i,name in enumerate(['Ana Martins','Daniel Ribeiro','Helena Duarte','Bruno Carvalho'])]
        trainees=[member('trainee.demo' if i==0 else f'trainee.{i}',name,'TRAINEE') for i,name in enumerate(['Lucas Almeida','Mariana Costa','Rafael Oliveira','Camila Rocha','Felipe Souza','Juliana Freitas','Pedro Nunes','Clara Mendes','Gabriel Lima','Luiza Barros'])]
        areas=[TrainingArea.objects.get_or_create(name=name,defaults={'description':desc})[0] for name,desc in [('Prática comunitária','Comunicação, acolhimento e trabalho em equipe.'),('Gestão de processos','Organização, planejamento e melhoria contínua.'),('Análise e qualidade','Investigação e acompanhamento de indicadores.')]]
        sites=[TrainingSite.objects.get_or_create(name=name,defaults={'city':'Cidade Horizonte'})[0] for name in ['Centro Aurora','Unidade Vila Verde','Núcleo Horizonte','Centro Integrado das Flores','Polo Jardim Norte']]
        periods=[RotationPeriod.objects.get_or_create(label=f'Ciclo {i+1} · {a.name}',defaults={'area':a,'starts_on':date(2026,8,3)+timedelta(days=28*i),'ends_on':date(2026,10,30)+timedelta(days=28*i)})[0] for i,a in enumerate(areas)]
        for i,t in enumerate(trainees):
            for j in range(2):
                placement,_=Placement.objects.get_or_create(trainee=t,site=sites[(i+j)%5],period=periods[(i+j)%3],defaults={'supervisor':supervisors[i%4],'active':True})
                for k in range(2):
                    Evaluation.objects.get_or_create(placement=placement,feedback=['Apresenta boa organização e comunicação clara. Próximo foco: ampliar a autonomia no planejamento das atividades.','Evolução consistente na prática supervisionada. Demonstra responsabilidade e incorpora o feedback recebido.'][k],defaults={'evaluator':placement.supervisor,'knowledge':3+(i+k)%3,'skills':3+(i+1)%3,'professionalism':4+i%2,'shared_with_trainee':True})
        Notice.objects.get_or_create(title='Acompanhamento do ciclo',defaults={'body':'Os supervisores já podem registrar o feedback formativo e compartilhar os próximos passos com cada trainee.'})
        self.stdout.write(self.style.SUCCESS('10 trainees, 4 supervisors, 5 sites, 3 periods and 40 evaluations ready.'))
