from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class Error(Exception):
    pass
class QuantityUnknown(Error):
    pass

class Ingredient(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    products = models.ManyToManyField('Product')

    def __unicode__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    ingredients = models.ManyToManyField(Ingredient)
    serves_min = models.IntegerField('Minimum number served', default=1)

    def __unicode__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    energy = models.FloatField('Energy per 100g (Cal)', null=True, blank=True)
    protein = models.FloatField('Protein %', null=True, blank=True)
    carb = models.FloatField('Carbohydrate %', null=True, blank=True)
    fat = models.FloatField('Fat %', null=True, blank=True)
    sodium = models.FloatField('Sodium %', null=True, blank=True)

    def __unicode__(self):
        return self.name

class Package(models.Model):
    product = models.ForeignKey(Product)
    barcode = models.CharField(max_length=15, null=True, blank=True)
    quantity = models.FloatField('quantity (g or ml)', null=True, blank=True)

    def __unicode__(self):
        return self.product.__unicode__() + ': ' + self.description

class Stock(models.Model):
    user = models.ForeignKey(User)
    package = models.ForeignKey(Package)
    fraction = models.FloatField(default=1.0, editable=False)
    use_date = models.DateField('use-by date', null=True, blank=True)

    def remove(self):
        self.fraction = 0.0
        self.save()

    def use_fraction(self, f):
        self.fraction -= f
        self.save()

    def use_fraction_current(self, f):
        self.use_fraction(f * self.fraction)

    def use_quantity(self, q):
        try:
            self.use_fraction(q / self.package.quantity)
        except TypeError:
            raise QuantityUnknown

    def get_quantity(self, q):
        try:
            return self.fraction * self.package.quantity
        except TypeError:
            raise QuantityUnknown

    def is_finished(self):
        return self.fraction <= 0.0

    def __unicode__(self):
        return self.package.__unicode__() + ' (%.0f%%)' % (100.0 * self.fraction)

def handle_stock_save(sender, instance, created, **kwargs):
    if created:
        instance.quantity = instance.package.quantity
        instance.save()
    if instance.is_finished():
        instance.delete()

post_save.connect(handle_stock_save, sender=Stock)