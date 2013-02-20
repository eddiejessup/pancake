from __future__ import print_function
import httplib, urllib

# Old deets
#HOST_SECURE = 'secure.techfortesco.com' # Seems to be dead (returns 900 error)
#HOST_UNSECURE = 'www.techfortesco.com' # Same, http version
#DEV_KEY = '7ISm4Lw5ZA9J9F5ieMw0' # Mine, mobile host says dev/app key not found
#APP_KEY = '15C0881129F58CA8CAF2' # See above

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

HOST = 'mobile.tesco.com'
API_PATH = 'groceryapi/restservice.aspx'
DEV_KEY = 'js6i90fvx21lp5cz4c2y'
APP_KEY = 'IG0HQ18NCOT5C47ML0OX'
EMAIL = 'elliot.marsden@gmail.com'
PASSWORD = 'fallout3'

#SESSION_KEY = 'EhaQ2E4Qzsotu9ZQj569skKIEA29I2utejHu32U3GKUmFe9Fk4'
SESSION_KEY = '42tkGvnAXaqxtayEQ46C874qIUruO9bbsUIOwqk9ohXYBoLOnq'

COMMAND = 'PRODUCTSEARCH'

PAGE = 1
SEARCHTEXT = '50184453'
EXTENDEDINFO = 'Y'

if COMMAND not in COMMANDS: raise Exception

args = [('command', COMMAND)]
if COMMAND == 'LOGIN':
    args += [('developerkey', DEV_KEY), ('applicationkey', APP_KEY),
             ('email', EMAIL), ('password', PASSWORD)]
elif COMMAND == 'LATESTAPPVERSION':
    args += [('appkey', APP_KEY)]
elif COMMAND == 'PRODUCTSEARCH':
    args += [('sessionkey', SESSION_KEY), ('page', PAGE),
             ('searchtext', SEARCHTEXT), ('extendedinfo', EXTENDEDINFO)]

path = '/' + API_PATH + '?' + urllib.urlencode(args)
#print(path)
conn = httplib.HTTPSConnection(HOST)
conn.request('GET', path)
results = conn.getresponse().read()
#print(results)

import json
a = json.loads(results)
print(a)
#for product in a['Products']:
#    for key in product.keys():
#        print(key, ': ', product[key])
#    print()

for nutrient in a['Products'][0]['Nutrients']:
    print(nutrient)
