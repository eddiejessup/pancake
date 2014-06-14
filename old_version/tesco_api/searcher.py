
import http.client
import urllib.request, urllib.parse, urllib.error
import json
import re

NUTRIENTS = (
    'Energy',
    'Protein',
    'Carbohydrates',
    'Carbohydrate',
    'Fat',
    'Sodium',
)

BARCODES = {
    'cordial': '5018374175182',
    'coffee': '7613033188404',
    'mackarel': '5000232213013',
    'marmite': '50184453',
    'mustard': '50147588',
    'sainstom': '01800951',
}

NAME_UNITS = {'m': {'g': ['G']},
              'v': {'L': ['L', 'Ltr', 'Litre'],
                    'cL': ['Cl'],
                    'mL': ['Ml']}}

SAMPLE_SIZE_UNITS = {'m': {'g': ['g']},
                     'v': {'mL': ['ml']}}

HOST = 'mobile.tesco.com'
API_PATH = 'groceryapi/restservice.aspx'
DEV_KEY = 'js6i90fvx21lp5cz4c2y'
APP_KEY = 'IG0HQ18NCOT5C47ML0OX'
EMAIL = 'elliot.marsden@gmail.com'
PASSWORD = 'fallout3'

SHITE_FIELDS = (
    'HealthierAlternativeProductId',
    'CarbonDataAvailable',
    'RDA_Saturates_Percent',
    'StorageInfo',
    'OfferID',
    'RDA_Calories_Count',
    'RDA_Fat_Grammes',
    'RDA_Saturates_Grammes',
    'MaximumPurchaseQuantity',
    'OfferValidity',
    'ExtendedDescription',
    'RDA_Calories_Percent',
    'RDA_Salt_Percent',
    'RDA_Fat_Percent',
    'OfferPromotion',
    'CheaperAlternativeProductId',
    'RDA_Sugar_Percent',
    'OfferLabelImagePath',
    'Rating',
    'CookingAndUsage',
    'RDA_Sugar_Grammes',
    'RDA_Salt_Grammes',
    'NutrientsCount',
    'ProductId',
    'IngredientsCount',
    'Ingredients',    
    'PriceDescription',
    'Price',
    'BaseProductId',
    'UnitPrice',
    'ImagePath',
)

class MultipleMatches(Exception): pass
class NoMatch(Exception): pass

def get_quantity(s, unit):
    if 'trace' in s.lower(): return 0.0
    if 'nil' in s.lower(): return 0.0
    a = re.findall(r'[0-9.]+ ?%s' % unit, s)
    if len(a) > 1: raise MultipleMatches
    elif len(a) == 1: return float(a[0].strip(unit))
    else: raise NoMatch


def parse_quantity_string(s, units):
    for measure in units:
        for unit in units[measure]:
            for spelling in units[measure][unit]:
                try:
                    amount = get_quantity(s, spelling)
                except NoMatch:
                    continue
                else:
                    measure = measure
                    unit = unit
                    return measure, unit, spelling, amount
    raise NoMatch

def get_conn():
    return http.client.HTTPSConnection(HOST)

def get_session_key(conn=None):
    args = [
        ('command', 'LOGIN'),
        ('developerkey', DEV_KEY),
        ('applicationkey', APP_KEY),
        ('email', EMAIL),
        ('password', PASSWORD),
    ]
    if conn is None: conn = get_conn()
    conn.request('GET', '/' + API_PATH + '?' + urllib.parse.urlencode(args))
    return json.loads(conn.getresponse().read())['SessionKey']

def barcode_to_prodpack(barcode, conn=None, session_key=None):
    args = [
        ('command', 'PRODUCTSEARCH'),
        ('page', '1'), 
        ('searchtext', barcode),        
    ]
    if conn is None: conn = get_conn()
    if session_key is None: session_key = get_session_key(conn)

    args.append(('sessionkey', session_key))
    conn.request('GET', '/' + API_PATH + '?' + urllib.parse.urlencode(args))
    results = json.loads(conn.getresponse().read())
    if results['TotalProductCount'] != 1:
        raise Exception('Found %i results' % results['TotalProductCount'])
    args.append(('extendedinfo', 'Y'))
    conn.request('GET', '/' + API_PATH + '?' + urllib.parse.urlencode(args))
    return json.loads(conn.getresponse().read())['Products'][0]

def print_prodpack(prodpack):
    print()
    for key in prodpack:
        if key != 'Nutrients' and key not in SHITE_FIELDS:
            print('\t%s: %s' % (key, prodpack[key]))
    print()
    for nutrient in prodpack['Nutrients']:
        nutrient_name = nutrient['NutrientName'].strip()
        print('\t%s (%s): %s' % (nutrient_name, 
                                 nutrient['SampleDescription'],
                                 nutrient['SampleSize']))
    print()

conn = get_conn()
session_key = get_session_key(conn)
prodpack = barcode_to_prodpack(BARCODES['sainstom'], conn, session_key)
#print_prodpack(prodpack)

name = prodpack['Name']
quantity_measure, quantity_unit, quantity_spelling, quantity_amount = parse_quantity_string(name, NAME_UNITS)
name = name.strip(str(quantity_amount) + quantity_spelling)

barcode = prodpack['EANBarcode']

for nutrient in prodpack['Nutrients']: 
    nutrient_name = nutrient['NutrientName'].lower()

    sample_size_measure, sample_size_unit, sample_size_spelling, sample_size_amount = parse_quantity_string(nutrient['SampleDescription'], SAMPLE_SIZE_UNITS)

    if 'energy' in nutrient_name:
        sample_result = get_quantity(nutrient['SampleSize'], 'kJ')
        energy = (100.0 / sample_size_amount) * sample_result
    elif 'protein' in nutrient_name:
        sample_result = get_quantity(nutrient['SampleSize'], 'g')
        protein = 100.0 * (sample_result / sample_size_amount)
    elif 'carb' in nutrient_name:
        sample_result = get_quantity(nutrient['SampleSize'], 'g')
        carbs = 100.0 * (sample_result / sample_size_amount)
    elif 'fat' in nutrient_name:
        sample_result = get_quantity(nutrient['SampleSize'], 'g')
        fat = 100.0 * (sample_result / sample_size_amount)      
    elif 'sodium' in nutrient_name:
        sample_result = get_quantity(nutrient['SampleSize'], 'g')
        sodium = 100.0 * (sample_result / sample_size_amount)

print()
print('\tProduct details:')
print('\tName: %s' % name)
print('\tEnergy: %s kJ per %s %s' % (energy, sample_size_amount, sample_size_unit))
print('\tProtein: %s g per %s %s' % (protein, sample_size_amount, sample_size_unit))
print('\tCarbohydrates: %s g per %s %s' % (carbs, sample_size_amount, sample_size_unit))
print('\tFat: %s g per %s %s' % (fat, sample_size_amount, sample_size_unit))
print('\tSodium: %s g per %s %s' % (sodium, sample_size_amount, sample_size_unit))
print()
print('\tPackage details:')
print('\tBarcode: %s' % barcode)
print('\tQuantity: %s %s' % (quantity_amount, quantity_unit))
print()
