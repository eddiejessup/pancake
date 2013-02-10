import re

class MultipleMatches(Exception): pass
class NoMatch(Exception): pass

class Measure(object):
    def __init__(self, name):
        self.name = name

class Unit(object):
    def __init__(self, measure, name, size, spellings):
        self.measure = measure
        self.name = name
        self.size = size
        self.spellings = spellings

class Quantity(object):
    def __init__(self, unit, amount):
        self.unit = unit
        self.amount = amount

    def get_amount_base(self):
        return self.unit.size * self.amount

MEASURES = {
    'mass': Measure('mass'),
    'volume': Measure('volume')
}

UNITS = [
    Unit(MEASURES['mass'], 'gram', 1.0, ['G']),
    Unit(MEASURES['volume'], 'millilitre', 1.0, ['Ml']),
    Unit(MEASURES['volume'], 'litre', 1000.0, ['L', 'Ltr', 'Litre']),
    Unit(MEASURES['volume'], 'centilitre', 100.0, ['Cl']),
]

def get_quantity(s, unit):
    a = re.findall(r'[0-9.]+ ?%s' % unit, s)
    if len(a) > 1: raise MultipleMatches
    elif len(a) == 1: return float(a[0].strip(unit))
    else: raise NoMatch

def parse_quantity_string(s):
    for unit in UNITS:
        for spelling in unit.spellings:
            try:
                amount = get_quantity(s, spelling)
            except NoMatch:
                continue
            else:
                s_stripped = s.strip('%s%s' % (str(amount), spelling)).strip()
                return Quantity(unit, amount), s_stripped
    raise NoMatch