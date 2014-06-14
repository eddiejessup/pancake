import re
import numpy as np

class Quantity(object):
    ''' A physical measurement, e.g. mass 
    '''
    def __init__(self, s, n):
        ''' s: short name
            n: long name
        '''
        self.s = s
        self.n = n
        self.us = []
        self.us_conv = {}

    def add_units(self, us_conv):
        self.us = list(us_conv.keys())
        self.us_conv = us_conv

    def get_amount(self, s):
        for unit in self.us:
            try:
                return unit.get_amount(s)
            except ValueError:
                pass
        raise ValueError

    def convert(self, u1, u2):
        return self.us_conv[u1][u2]

    def __repr__(self):
        return self.n

class Unit(object):
    ''' A fixed size of a quantity, e.g. a gram. 
    '''
    def __init__(self, s, q, re=None):
        ''' s:  short name
            re: regular expression for strings representing samples in the 
                unit
            re: regular expression for strings representing samples in the 
                unit
        '''
        self.s = s
        self.q = q
        self.re = re

    def get_amount(self, s):
        m = re.search(self.re, s)
        if m:
            # Detect for unit being trace
            if self.s == 't': size = 0.0
            else: size = float(m.group(0))
            return Amount(self, size)
        raise ValueError

    def __repr__(self):
        return self.s

class Amount(object):
    ''' A unit and the associated magnitude in that unit, e.g. 100 grams '''
    def __init__(self, u, m):
        ''' u: a unit
            m: a magnitude
        '''
        self.u = u
        self.m = m

    def __add__(self, other):
        if self.u.q is not other.u.q:
            raise TypeError('Can only add amounts of the same quantity')
        m = self.m + other.m *  self.u.q.convert(other.u, self.u)
        return Amount(self.u, m)

    def __sub__(self, other):
        if self.u.q is not other.u.q:
            raise TypeError('Can only subtract amounts of the same quantity')
        m = self.m - other.m *  self.u.q.convert(other.u, self.u)
        return Amount(self.u, m)

    # Massively hacky, just to be able to sum a list of amounts
    def __radd__(self, other):
        return self

    def convert(self, u):
        return self.m * self.u.q.convert(self.u, u)

    def __repr__(self):
        return '%g%s' % (self.m, self.u)

class Substance(object):
    ''' A category of matter, e.g. protein.
    '''
    def __init__(self, s, n, q, re=''):
        ''' s:  short name
            n:  long name
            re: regular expression for strings representing samples of the 
                substance
        '''
        self.s = s
        self.n = n
        self.re = re
        self.q = q

    def matches(self, s):
        return re.search(self.re, s)

    def __repr__(self):
        return self.n

class Sample(object):
    ''' An amount of a substance, e.g. 100 grams of protein
    '''
    def __init__(self, subs, am):
        self.subs = subs
        self.am = am

    def __add__(self, other):
        if self.subs is not other.subs:
            raise TypeError('Can only add samples of the same substance')
        return Sample(self.subs, self.am + other.am)

    def __add__(self, other):
        if self.subs is not other.subs:
            raise TypeError('Can only subtract samples of the same substance')
        return Sample(self.subs, self.am - other.am)

    def __repr__(self):
        return '%s of %s' % (self.am, self.subs)

re_real = '\d*\.?\d+'

mass = Quantity('m', 'Mass')
gram = Unit('g', mass, '%s(?= *[gG](ram)?)' % re_real)
trace = Unit('t', mass, '[Tt]race')
mass_conv = {}
mass_conv[gram] = {trace: np.inf, gram: 1.0}
mass_conv[trace] = {gram: 1.0 / mass_conv[gram][trace], trace: 1.0}
mass.add_units(mass_conv)

energy = Quantity('e', 'Energy')
kj = Unit('kj', energy, '%s(?= *[kK][jJ])' % re_real)
kcal = Unit('kcal', energy, '%s(?= *[kK][cC](al|AL)?)' % re_real)
energy_conv = {}
energy_conv[kj] = {kj: 1.0, kcal: 0.239}
energy_conv[kcal] = {kj: 1.0 / energy_conv[kj][kcal], kcal: 1.0}
energy.add_units(energy_conv)

protein = Substance('p', 'Protein', mass, '[pP]rotein')
carb = Substance('c', 'Carbohydrate', mass, '[cC]arbohydrate')
fat = Substance('f', 'Fat', mass, '[fF]at')
fibre = Substance('b', 'Fibre', mass, '[fF]ibre')
salt = Substance('s', 'Salt', mass, '[sS]alt')
water = Substance('w', 'Water', mass, '[wW]ater')
nutrients = [
    protein,
    carb,
    fat,
    fibre,
    salt,
    water,
]