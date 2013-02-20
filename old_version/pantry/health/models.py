import datetime
from django.db import models
from django.contrib.auth.models import User

def calc_bmi(w, h):
    return w / h ** 2

def calc_bmr(g, w, h, a):
    ''' Basal metabolic rate as calculated from Revised Harris-Benedict equation '''
    if g == 'M':
        return 13.397 * w + 479.9 * h - 5.677 * a + 88.362
    elif g == 'F':
        return 9.247 * w + 309.8 * h - 4.330 * a + 447.593
    else:
        raise Exception

class Exercise(models.Model):
    name = models.CharField(max_length=30)
    energy_distance = models.FloatField('Calories per kg per km', null=True, blank=True)
    energy_time = models.FloatField('Calories per kg per min', null=True, blank=True)
    energy_unit = models.FloatField('Calories per kg per unit', null=True, blank=True)
    aerobic = models.BooleanField()

class ActivityLog(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField('activity Date', default=datetime.date.today)    
    description = models.CharField(max_length=30)    
    energy = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)
    carb = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    salt = models.FloatField(null=True, blank=True)

    @staticmethod
    def get_net_energy(user, date):
        bmr = HealthLog.calc_bmr(user, date)
        nonbmr = sum((a.energy for a in ActivityLog.objects.filter(date__exact=date).filter(user__pk=user.pk)))
        return nonbmr - bmr

class HealthLog(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField('activity Date', default=datetime.date.today)    
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    fat = models.FloatField("fat percentage", null=True, blank=True)
    muscle = models.FloatField("muscle percentage", null=True, blank=True)
    water = models.FloatField("water percentage", null=True, blank=True)

    @staticmethod
    def calc_weight(user, date):
        # Big stub
        return HealthLog.objects.filter(date__exact=date).filter(user__pk=user.pk).order_by('date')[0].weight

    @staticmethod    
    def calc_height(user, date):
        # Big stub
        return HealthLog.objects.filter(date__exact=date).filter(user__pk=user.pk).order_by('date')[0].height

    @staticmethod    
    def calc_bmi(user, date):
        return calc_bmi(HealthLog.calc_weight(user, date), HealthLog.calc_height(user, date))

    @staticmethod    
    def calc_bmr(user, date):
        return calc_bmr(user.userprofile.gender, HealthLog.calc_weight(user, date), HealthLog.calc_height(user, date), user.get_age(date))
