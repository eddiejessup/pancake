from pantry.stocks.models import Product, Package, Stock, Recipe, Ingredient
from django.contrib import admin

admin.site.register(Product)
admin.site.register(Package)
admin.site.register(Stock)
admin.site.register(Recipe)
admin.site.register(Ingredient)