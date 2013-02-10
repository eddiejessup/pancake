from __future__ import print_function
import httplib
import urllib
import json

BARCODES = {
    'cordial': '5018374175182',
    'coffee': '7613033188404',
    'mackarel': '5000232213013',
    'marmite': '50184453',
    'mustard': '50147588',
    'sainstom': '01800951',
}

COMMANDS = (
    'AMENDORDER',
    'CANCELAMENDORDER',
    'CHANGEBASKET',
    'CHOOSEDELIVERYSLOT',
    'LATESTAPPVERSION',
    'LISTBASKET',
    'LISTBASKETSUMMARY',
    'LISTDELIVERYSLOTS',
    'LISTFAVOURITES',
    'LISTPENDINGORDERS',
    'LISTPRODUCTCATEGORIES',
    'LISTPRODUCTOFFERS',
    'LISTPRODUCTSBYCATEGORY',
    'LOGIN',
    'PRODUCTSEARCH',
    'READYFORCHECKOUT',
    'SAVEAMENDORDER',
    'SERVERDATETIME',
)

class TescoSearcher(object):
    UNWANTED_FIELDS = (
        'CarbonDataAvailable',
        'CheaperAlternativeProductId',
        'CookingAndUsage',
        'HealthierAlternativeProductId',
        'MaximumPurchaseQuantity',
        'OfferID',
        'OfferLabelImagePath',
        'OfferPromotion',
        'OfferValidity',
        'Price',
        'PriceDescription',
        'Rating',
        'UnitPrice',
    )

    NUTRIENT_FIELDS = (
        'Nutrients',
        'NutrientsCount',
        'RDA_Calories_Count',
        'RDA_Calories_Percent',
        'RDA_Saturates_Grammes',
        'RDA_Saturates_Percent',
        'RDA_Fat_Grammes',
        'RDA_Fat_Percent',
        'RDA_Salt_Grammes',
        'RDA_Salt_Percent',
        'RDA_Sugar_Grammes',
        'RDA_Sugar_Percent',
    )

    HIDDEN_FIELDS = (
        'EANBarcode',
        'ProductId',
        'ProductType',
        'BaseProductId',
        'UnitType',
        'ImagePath',
    )

    HOST = 'mobile.tesco.com'
    API_PATH = 'groceryapi/restservice.aspx'
    DEV_KEY = 'js6i90fvx21lp5cz4c2y'
    APP_KEY = 'IG0HQ18NCOT5C47ML0OX'

    def __init__(self, email=None, password=None):
        self.args_base = {
            'developerkey': self.DEV_KEY,
            'applicationkey': self.APP_KEY,
        }
        self.conn =  httplib.HTTPSConnection(self.HOST)
        self.get_path_base()
        self.login()

    def login(self):
        args = {
            'command': 'LOGIN',
            'email': '',
            'password': '',
        }
        session_key = self.get_response(args)['SessionKey']
        self.args_base['sessionkey'] = session_key
        self.get_path_base()

    def get_path_base(self):
        self.path_base = '/%s?%s' % (self.API_PATH, urllib.urlencode(self.args_base))

    def get_response(self, args):
        self.conn.request('GET', '%s&%s' % (self.path_base, urllib.urlencode(args)))
        return json.loads(self.conn.getresponse().read())

    def filter(self, results):
        results_filtered = {'misc': {}, 'nutrients': {}, 'hidden': {}}
        for key in results:
            if key in self.UNWANTED_FIELDS:
                pass
            elif key in self.NUTRIENT_FIELDS:
                results_filtered['nutrients'][key] = results[key]
            elif key in self.HIDDEN_FIELDS:
                results_filtered['hidden'][key] = results[key]
            else:
                results_filtered['misc'][key] = results[key]
        return results_filtered

    def search(self, query):
        args = {
            'command': 'PRODUCTSEARCH',
            'page': '1',
            'searchtext': query,
        }
        results = self.get_response(args)
        if results['TotalProductCount'] > 1:
            print('Found %i results' % results['TotalProductCount'])
            return None
        elif results['TotalProductCount'] == 0:
            return None
        else:
            args['extendedinfo'] = 'Y'
            results = self.get_response(args)['Products'][0]
            return self.filter(results)