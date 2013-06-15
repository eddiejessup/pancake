from __future__ import print_function
import re
import httplib
import urllib
import json
import numpy as np

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
        'StorageInfo',
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
        'IngredientsCount',
        'NutrientsCount',
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

    def filter(self, res):
        resf = {}
        for key in res:
            if key not in self.UNWANTED_FIELDS:
                resf[key] = res[key]
        return resf

    def search(self, query):
        args = {
            'command': 'PRODUCTSEARCH',
            'page': '1',
            'searchtext': query,
        }
        results = self.get_response(args)
        if results['TotalProductCount'] > 1:
            print('Found %i results:' % results['TotalProductCount'])
            for result in results['Products']:
                print(result['Name'])
            return None
        elif results['TotalProductCount'] == 0:
            return None
        else:
            args['extendedinfo'] = 'Y'
            results = self.get_response(args)['Products'][0]
            results = self.filter(results)
            return results