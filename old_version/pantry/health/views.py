import datetime
from django import forms
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.auth.models import User
from django.core import serializers
from pantry.health.models import HealthLog, ActivityLog, Exercise
from pantry.stocks.models import Product

def home(request):
    return HttpResponseRedirect(reverse('activity_log_add'))

class HealthLogForm(forms.ModelForm):
    class Meta:
        model = HealthLog

class ActivityLogForm(forms.Form):
    user = forms.ModelChoiceField(User.objects.all())
    date = forms.DateField(initial=datetime.date.today)
    description = forms.CharField(max_length=30)
    ACTIVITY_CHOICES = (('F', 'Food'), ('E', 'Exercise'))
    activity = forms.ChoiceField(ACTIVITY_CHOICES, initial='F')

    product = forms.ModelChoiceField(Product.objects.all(), required=False)
    product_quantity = forms.FloatField(required=False)
    
    exercise = forms.ModelChoiceField(Exercise.objects.all(), required=False)
    EXERCISE_MEASURE_CHOICES = (('T', 'Time'), ('D', 'Distance'), ('U', 'Units'), ('E', 'Energy'))
    exercise_measure = forms.ChoiceField(EXERCISE_MEASURE_CHOICES)
    exercise_quantity = forms.FloatField(required=False)

    energy = forms.FloatField(required=False)
    carb = forms.FloatField('carbohydrate', required=False)
    fat = forms.FloatField(required=False)
    protein = forms.FloatField(required=False)
    salt = forms.FloatField(required=False)

@login_required
def activity_log_add(request):
    if request.method == 'POST':
        form = ActivityLogForm(request.POST)
        if form.is_valid():
            a = ActivityLog(user=request.user, date=form.cleaned_data['date'], description=form.cleaned_data['description'], 
                            energy=form.cleaned_data['energy'], fat=form.cleaned_data['fat'], carb=form.cleaned_data['carb'],
                            protein=form.cleaned_data['protein'], salt=form.cleaned_data['salt'])
            a.save()
            return 
    else:
        form = ActivityLogForm()
    return render(request, 'health/activity_log_add.html', {
        'form': form,
        'products': Product.objects.all()
    })

def activity_log_home(request):
    return HttpResponseRedirect(reverse('activity_log_add'))

def ajax_get_exercise(request):
    if request.is_ajax() and request.method == 'GET':
        exercise = Exercise.objects.get(pk=request.GET['pk'])
        data = serializers.serialize('json', [exercise], ensure_ascii=False)
        return HttpResponse(data, 'application/javascript')
    return HttpResponse(status=400)    