from django import forms
from django.forms.formsets import formset_factory
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, NoReverseMatch
from django.core import serializers
from django.views.generic.edit import CreateView

from pantry.stocks.models import Product, Package, Stock, QuantityUnknown

def stocks_equivalent(s_1, s_2):
    if s_1.use_date != s_2.use_date: return False
    if s_1.fraction != s_2.fraction: return False
    return True

class BarcodeForm(forms.Form):
    barcode = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

class AddStockForm(forms.Form):
    barcode = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'autofocus': 'autofocus'}), required=False)
    package = forms.ModelChoiceField(Package.objects.all(), required=False)
    use_date = forms.DateField(label='Use-by date', required=False)

class UseStockForm(forms.Form):
    measure_choices = (
        ('I', 'Initial stock fraction'),
        ('C', 'Current stock fraction'),
        ('Q', 'Quantity'),
    )
    measure = forms.ChoiceField(measure_choices, initial='I', label='Measuring unit')
    delta = forms.FloatField(label='Amount', initial=1.0, widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package

def home(request):
    if request.method == 'GET':
        form = BarcodeForm(request.GET)
        if form.is_valid():
            barcode = form.cleaned_data['barcode']
            if request.GET['operation'] == 'Search':
                return HttpResponseRedirect(reverse('search_stock', args=(barcode,)))
            elif request.GET['operation'] == 'Lookup':
                return HttpResponseRedirect(reverse('barcode_lookup', args=(barcode,)))
            else:
                raise Exception
    else:
        form = BarcodeForm()

    args = {'form': form}
    if request.user.is_authenticated():
        args['stocks'] = Stock.objects.filter(user__pk=request.user.pk)
    else:
        args['stocks'] = None
    return render(request, 'stocks/home.html', args)

@login_required
def search(request, barcode):
    results = Stock.objects.filter(user__pk=request.user.pk).filter(package__barcode=barcode)

    # Remove duplicates
    dupes = []
    for i_1 in range(len(results)):
        for i_2 in range(i_1 + 1, len(results)):
            if stocks_equivalent(results[i_1], results[i_2]):
                dupes.append(results[i_2])
    for dupe in dupes: results = results.exclude(pk=dupe.pk)

    if len(results) == 0:
        messages.info(request, 'No stocks found with this barcode!')
        return HttpResponseRedirect(reverse('home'))
    elif len(results) == 1:
        return HttpResponseRedirect(reverse('use_stock', args=(results[0].id,)))
    else:
        return render(request, 'stocks/barcode_search_results.html', {
            'results': results})

def lookup(request, barcode):
    try:
        import barcode_scanner
    except ImportError:
        messages.error(request, 'Barcode lookup not available')
        return HttpResponseRedirect(reverse('home'))
    try:
        results = barcode_scanner.barcode_lookup('ean', barcode)
    except barcode_scanner.LookupFailed:
        messages.error(request, 'Lookup failed!')
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'stocks/barcode_lookup_results.html', {
        'results': results})

@login_required
def use(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        if 'remove' in request.POST.keys():
            stock.remove()
            messages.info(request, 'Stock finished!')
            form = UseStockForm()
            return HttpResponseRedirect(reverse('home'))
        elif 'use' in request.POST.keys():
            form = UseStockForm(request.POST)
            if form.is_valid():
                measure = form.cleaned_data['measure']
                delta = form.cleaned_data['delta']
                if measure == 'I':
                    stock.use_fraction(delta)
                elif measure == 'C':
                    stock.use_fraction_current(delta)
                elif measure == 'Q':
                    try:
                        stock.use_quantity(delta)
                    except QuantityUnknown:
                        messages.error('Package quantity unknown!')
                        return HttpResponseRedirect(reverse('home'))
                try:
                    newpath = reverse('use_stock', args=(stock.id,))
                except NoReverseMatch:
                    messages.info(request, 'Stock finished!')
                    newpath = reverse('home')
                else:
                    messages.info(request, 'Stock used!')
                return HttpResponseRedirect(newpath)
        else:
            raise Exception
    else:
        form = UseStockForm()

    return render(request, 'stocks/use.html', {
        'stock': stock,
        'form': form,
    })

@login_required
def add(request):
    if request.method == 'POST':
        form = AddStockForm(request.POST)
        if form.is_valid():
            if request.POST['operation'] == 'Add from barcode':
                try:
                    package = Package.objects.get(barcode=form.cleaned_data['barcode'])
                except Package.DoesNotExist:
                    messages.error(request, 'Barcode not found!')
                    return HttpResponseRedirect(reverse('add_stock'))
            elif request.POST['operation'] == 'Add from list':
                package = form.cleaned_data['package']
                if package is None:
                    messages.error(request, 'No package stock selected!')
                    return HttpResponseRedirect(reverse('add_stock'))
            else:
                raise Exception
            s = Stock(user=request.user, package=package, use_date=form.cleaned_data['use_date'])
            s.save()
            messages.success(request, 'Stock added!')
            return HttpResponseRedirect(reverse('add_stock'))
    else:
        form = AddStockForm()
    return render(request, 'stocks/add.html', {
        'form': form,
    })

#@login_required
class StockCreate(CreateView):
    model = Stock
    template_name = 'stocks/add.html'

def add_prodpacks(request):
    PackageFormSet = formset_factory(PackageForm, extra=2)
    if request.method == 'POST':
        prod_form = ProductForm(request.POST)
        package_formset = PackageFormSet(request.POST, request.FILES)
        if prod_form.is_valid() and package_formset.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        prod_form = ProductForm()
        package_formset = PackageFormSet()

    return render(request, 'stocks/addprodpacks.html', {
        'prod_form': prod_form,
        'package_formset': package_formset,
    })

def ajax_get_product(request):
    if request.is_ajax() and request.method == 'GET':
        product = Product.objects.get(pk=request.GET['pk'])
        data = serializers.serialize('json', [product], ensure_ascii=False)
        return HttpResponse(data, 'application/javascript')
    return HttpResponse(status=400)