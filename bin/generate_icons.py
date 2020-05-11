#!/usr/bin/env python3
import argparse
import csv
import math
import re
import shutil
from pathlib import Path

from bs4 import BeautifulSoup

from svg_effects import glow
from svg_render import render

parser = argparse.ArgumentParser(description='Generate icon theme from SVG template.')
parser.add_argument('-v', '--verbose', action='store_true', help='Increase verbosity')
parser.add_argument('-o', '--out', help='Output folder', default='build/glow')
parser.add_argument('-a', '--app-ids', help='CSV of app ids', default='source/app_ids.csv')
parser.add_argument('-p', '--plist', help='Path to Info.plist', default='source/Info.plist')
parser.add_argument('svgs', nargs='+', help='SVG files to render')

args = parser.parse_args()
VERBOSE = args.verbose
OUT = Path(args.out)

def vprint(*args, end='\n'):
  if VERBOSE: print(*args, end=end)

def read_app_ids(file):
  bundles = {}
  with open(file, newline='') as csv_file:
    read = csv.reader(csv_file)
    for name, bundle_id in read:
      if name not in bundles:
        bundles[name] = [bundle_id]
      else:
        bundles[name].append(bundle_id)

  print(f'Read {len(bundles)} app names for {sum(len(x) for x in bundles.values())} icons.')
  vprint('Duplicates:')
  for name, ids in bundles.items():
    if len(ids) > 1:
      vprint(f'  {name}: {", ".join(ids)}')
  return bundles

def read_template(icon, app_ids):
  name = re.sub(r'_x([0-9A-F]+)_',
    lambda match: chr(int(match.group(1), 16)), icon['id'])
  if name.endswith('_'):
    name = ' '.join(name.split('_')[:-2])
  icon['id'] = name

  if name not in app_ids:
    raise NotImplementedError(f'App ID not found for {name} ({icon["id"]}).')
  return icon, app_ids[name]

out_path = Path(OUT, 'IconBundles')
print(f'Initializing output directory {out_path}.')
if out_path.exists():
  shutil.rmtree(out_path)
Path.mkdir(out_path, parents=True)
shutil.copyfile(args.plist, Path(OUT, 'Info.plist'))

app_ids = read_app_ids(args.app_ids)

for svgfile in args.svgs:
  print(f'Rendering icons in {svgfile}')
  soup = BeautifulSoup(open(svgfile), 'xml').svg
  [icon_g] = soup('g', id='Icons')
  icons = icon_g('g', recursive=False)[::-1]
  for i in range(len(icons)):
    grid = (i%12 + 1, math.floor(i/12) + 1)

    vprint(f'Rendering a:{grid[0]}:{grid[1]} - ', end='')
    try:
      icon, gids = read_template(icons[i], app_ids)
    except NotImplementedError as e:
      print(f'WARN: Icon {grid[0]}:{grid[1]} marked as unknown. Skipping.')
      continue

    vprint(f'{gids} ({icon["id"]})...', end='')
    png = render(icon, soup.style, grid, effect=glow())
    for fname in gids:
      fpath = Path(out_path, f'{fname}-large.png')
      with open(fpath, mode='w+b') as f:
        f.write(png)
        print('.', end='', flush=True)
    vprint()
  print(f'\nFinished rendering {len(icons)} icons.')
