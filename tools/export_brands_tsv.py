"""Exports brands.bin (BRN2) to the readable brands.tsv for the open data page. Usage: python tools/export_brands_tsv.py <brands.bin> <brands.tsv>"""
import struct, sys
src, out = sys.argv[1], sys.argv[2]
b = open(src, 'rb').read()
assert b[:4] == b'BRN2'
n = struct.unpack_from('<I', b, 4)[0]
cats = "FRUIT_VEG BAKERY DAIRY_EGGS MEAT_FISH FROZEN_READY PANTRY COOKING_BAKING BREAKFAST_SNACKS BEVERAGES PERSONAL_CARE_HEALTH CLEANING_LAUNDRY HOME_GARDEN BABY_TOYS CLOTHING_SPORTS PETS".split()
lines = ["# MiBeN Shopping List - category suggestion table (market, key, category code, confidence %)",
         "# Contains data from Open Food Facts (https://world.openfoodfacts.org), (c) Open Food Facts contributors, ODbL 1.0 (https://opendatacommons.org/licenses/odbl/1-0/)",
         "# This table is released under the same licence. Category 0 in a market section = the key is suppressed in that market.",
         "# Categories: " + ", ".join(f"{i+1}={c}" for i, c in enumerate(cats)),
         "market\tkey\tcategory\tconfidence"]
for i in range(n):
    o = 8 + 24 * i
    name = b[o:o+16].rstrip(b'\0').decode(); pos, ln = struct.unpack_from('<II', b, o + 16)
    s = b[pos:pos+ln]; assert s[:4] == b'BRN1'
    cnt, tot = struct.unpack_from('<II', s, 4)
    offs = struct.unpack_from('<%dI' % (cnt + 1), s, 12)
    kb = 12 + 4 * (cnt + 1); vb = kb + tot
    for k in range(cnt):
        key = s[kb+offs[k]:kb+offs[k+1]].decode()
        lines.append(f"{name}\t{key}\t{s[vb+2*k]}\t{s[vb+2*k+1]}")
open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print(len(lines) - 5, 'rows')
