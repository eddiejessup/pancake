from django.db import models
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse

class Error(Exception):
    pass
class QuantityUnknown(Error):
    pass

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.pk})

class Package(models.Model):
    product = models.ForeignKey(Product)
    barcode = models.CharField(max_length=15, null=True, blank=True, unique=True)
    quantity = models.FloatField('quantity (g)', null=True, blank=True)

    def __unicode__(self):
        return '%s, [%s], %s' % (self.product.__unicode__(), self.barcode, self.quantity)

    def quantity_str(self):
        return '%sg' % self.quantity

class Stock(models.Model):
    package = models.ForeignKey(Package)
    fraction = models.FloatField(default=1.0, editable=False)

    def equivalent(self, stock):
        if self.package is not stock.package: return False
        if self.fraction != stock.fraction: return False
        return True

    def use_fraction(self, f):
        self.fraction -= f
        self.save()

    def get_quantity(self, q):
        try:
            return self.fraction * self.package.quantity
        except TypeError:
            raise QuantityUnknown

    def is_finished(self):
        return self.fraction <= 0.0

    def __unicode__(self):
        return ('%s (%.0f%%)' % (self.package.__unicode__(), 100.0 * self.fraction))

    def get_absolute_url(self):
        return reverse('stock-detail', kwargs={'pk': self.pk})

    @staticmethod
    def get_absolute_model_url():
        return reverse('stock-list')


def handle_stock_save(sender, instance, created, **kwargs):
    if created:
        instance.quantity = instance.package.quantity
        instance.save()
    if instance.is_finished():
        instance.delete()

post_save.connect(handle_stock_save, sender=Stock)