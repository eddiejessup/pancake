from django import forms
from django.forms import ModelForm
from django.forms.models import modelformset_factory, inlineformset_factory
from django.shortcuts import render
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, FormView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.create_update import create_object
from django.contrib import messages
from store.models import Product, Package, Stock
import tesco.search, tesco.parse

def home(request):
    return render(request, 'store/home.html')


class ProductList(ListView):
    model = Product

class ProductDetail(DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context['packages'] = Package.objects.filter(product_id__exact=self.kwargs['pk'])
        return context

class ProductForm(ModelForm):
    class Meta:
        model = Product

def product_update(request, pk=None):
    FormSet = inlineformset_factory(Product, Package, extra=1)

    # pk is None means we're making a new product
    if pk is not None:
        product = Product.objects.get(pk=pk)
    else: product = None

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        if product_form.is_valid():
            product = product_form.save(commit=False)
            formset = FormSet(request.POST, request.FILES, instance=product)
            if formset.is_valid():
                product.save()
                formset.save()
                return HttpResponseRedirect(product.get_absolute_url())
        else:
            formset = FormSet()
    else:
        if 'initial_product_fields' in request.session.keys():
            product_initial = request.session['initial_product_fields']['product']
            package_initial = request.session['initial_product_fields']['package']
        else:
            product_initial = package_initial = None
        product_form = ProductForm(initial=product_initial)
        formset = FormSet(instance=product, initial=package_initial)
    return render(request, 'store/product_form.html', {'formset': formset, 'product_form': product_form})

class StockList(ListView):
    model = Stock

class StockDetail(DetailView):
    model = Stock

class StockCreate(CreateView):
    model = Stock

class StockUpdateForm(forms.Form):
    delta = forms.FloatField(label='Fraction', initial=1.0)

class StockUpdate(FormView):
    template_name = 'store/stock_form.html'
    form_class = StockUpdateForm

    def get_context_data(self, **kwargs):
        context = super(StockUpdate, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        stock = Stock.objects.get(pk=self.kwargs['pk'])
        stock.use_fraction(form.cleaned_data['delta'])
        if stock.is_finished():
            return HttpResponseRedirect(Stock.get_absolute_model_url())
        else:
            return HttpResponseRedirect(stock.get_absolute_url())


def remove_duplicates(objects):
    duplicates = []
    for i_1 in range(len(objects)):
        for i_2 in range(i_1 + 1, len(objects)):
            if objects[i_1].equivalent(objects[i_2]):
                duplicates.append(objects[i_2])
    for object in duplicates: objects = objects.exclude(pk=object.pk)

class BarcodeForm(forms.Form):
    barcode = forms.CharField(max_length=15)

class ProductSearchBarcode(FormView):
    template_name = 'store/search_barcode.html'
    form_class = BarcodeForm

    def form_valid(self, form):
        try:
            product = Package.objects.get(barcode=form.cleaned_data['barcode']).product
        except Package.DoesNotExist:
            messages.info(self.request, 'No product found with this barcode!')
            return HttpResponseRedirect(reverse('product-search-barcode'))
        return HttpResponseRedirect(product.get_absolute_url())

class StockSearchBarcode(FormView):
    template_name = 'store/search_barcode.html'
    form_class = BarcodeForm

    def form_valid(self, form):
        stocks = Stock.objects.filter(package__barcode=form.cleaned_data['barcode'])
        remove_duplicates(stocks)

        if len(stocks) == 0:
            messages.info(self.request, 'No stocks found with this barcode!')
            return HttpResponseRedirect(reverse('stock-search-barcode'))
        else:
            return render(self.request, 'store/stock_search_results.html', {'object_list': stocks})

class ProductLookup(FormView):
    template_name = 'store/search_barcode.html'
    form_class = BarcodeForm

    def form_valid(self, form):
        searcher = tesco.search.TescoSearcher()
        results = searcher.search(form.cleaned_data['barcode'])
        self.request.session['initial_product_fields'] = lookup_to_product(results)
        return render(self.request, 'store/product_lookup_results.html', {'results': results})

def lookup_to_product(results):
    fields = {'product': {}, 'package': [{}]}
    quantity, name = tesco.parse.parse_quantity_string(results['misc']['Name'])
    fields['product']['name'] = name
    fields['package'][0]['quantity'] = quantity.get_amount_base()
    fields['package'][0]['barcode'] = results['hidden']['EANBarcode']
    return fields