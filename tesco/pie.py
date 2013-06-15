import re
import search
from base import *

def pretty(d, indent=1):
   for key, value in d.iteritems():
      print('  ' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent + 1)
      else:
         print('  ' * (indent + 1) + str(value))

def nutrient_pie(result):
    def get_total_amount(s_subs, s_amount):
        # Look for a match to e.g. (100g) in sample description
        try:
            amount = mass.get_amount(s_amount)
        except ValueError:
            m = re.search('(?<=Typical values per ).+', s_amount)
            if m and m.group(0) == 'can':
                amount = mass.get_amount(s_subs)
        return amount

    s_nuts = result['Nutrients']
    s_subs_tot = result['Name']
    s_amount_tot = s_nuts[0]['SampleDescription']

    samples = []
    for s_nut in s_nuts:
        s_subs = s_nut['NutrientName']
        s_amount = s_nut['SampleSize']
        # print(s_subs, s_amount, s_nut['SampleDescription'])
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

if __name__ == '__main__':
    ts = search.TescoSearcher()
    # res = ts.search('Sunpat Peanut Butter Crunchy 454G')
    # res = ts.search('John West Tuna Steaks In Brine 130G')
    # res = ts.search('Jacobs Twiglets 150G')
    # res = ts.search('Heinz Baked Beans 3X200g')
    res = ts.search('Tesco Cherry Tomatoes 300G')

    samples = nutrient_pie(res)

    pretty(res)

    import pylab as pp
    mass_samples = [s for s in samples if s.am.u.q is mass]
    # print(samples)
    sample_grams = [s.am.convert(gram) for s in mass_samples]
    sample_subs = [s.subs for s in mass_samples]

    fig = pp.figure()
    ax = fig.gca()
    ax.set_aspect('equal')
    ax.pie(sample_grams, labels=sample_subs)
    pp.show()