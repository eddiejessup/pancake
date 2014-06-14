import re
import pylab as pp
from . import search
from .base import *

def pretty(d, indent=1):
   for key, value in d.items():
      print('  ' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent + 1)
      else:
         print('  ' * (indent + 1) + str(value))

def get_total_amount(s_subs, s_amount):
    try:
        amount = mass.get_amount(s_amount)
    except ValueError:
        m = re.search('(?<=Typical values per ).+', s_amount)
        if m and m.group(0) == 'can':
            amount = mass.get_amount(s_subs)
    return amount

def nutrient_pie(result):
    s_nuts = result['Nutrients']
    s_subs_tot = result['Name']
    s_amount_tot = s_nuts[0]['SampleDescription']

    samples = []
    for s_nut in s_nuts:
        s_subs = s_nut['NutrientName']
        s_amount = s_nut['SampleSize']
        for nut in nutrients:
            if nut.matches(s_subs):
                try:
                    amount = nut.q.get_amount(s_amount)
                except ValueError:
                    continue
                sample = Sample(nut, amount)
                samples.append(sample)
                break

    amount_found = sum([s.am for s in samples if s.am.u.q is mass])
    subs_tot = Substance('t', s_subs_tot, mass)
    amount_tot = get_total_amount(s_subs_tot, s_amount_tot)
    sample_tot = Sample(subs_tot, amount_tot)
    sample_water = Sample(water, sample_tot.am - amount_found)
    samples.append(sample_water)
    return samples

def plot_pie(samples):
    mass_samples = [s for s in samples if s.am.u.q is mass]
    sample_grams = [s.am.convert(gram) for s in mass_samples]
    sample_subs = [s.subs for s in mass_samples]

    fig = pp.figure()
    ax = fig.gca()
    ax.set_aspect('equal')
    ax.pie(sample_grams, labels=sample_subs)
    pp.show()    

def query_to_plot(query):
    res = search.single_search(query)
    samples = nutrient_pie(res)
    plot_pie(samples)

if __name__ == '__main__':
    # query = 'Tesco Cherry Tomatoes 300G'
    # query = 'Sunpat Peanut Butter Crunchy 454G'
    # query = 'John West Tuna Steaks In Brine 130G'
    # query = 'Jacobs Twiglets 150G'
    query = '/Heinz Baked Beans 3X200g'
    query_to_plot(query)