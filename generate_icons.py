#!/usr/bin/env python3
import csv, re, math, os, shutil
from bs4 import BeautifulSoup
from cairosvg import svg2png
from pathlib import Path

VERBOSE = False

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

def read_svg(icon, app_ids):
  name = re.sub(r'_x([0-9A-F]+)_',
    lambda match: chr(int(match.group(1), 16)), icon['id'])
  if name.endswith('_'):
    name = ' '.join(name.split('_')[:-2])
  icon['id'] = name

  if name not in app_ids:
    raise NotImplementedError(f'App ID not found for {name} ({icon["id"]}).')
  return icon, app_ids[name]

def render_svg(g, style, grid, glow=0):
  try:
    coords = (440 + grid[0]*1080 + 90, 440 + grid[1]*1080 + 90) 
    svg = f"""
      <svg
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        viewBox="{coords[0]} {coords[1]} 900 900"
      >
        {style}
        <filter id="glow">
          <feGaussianBlur stdDeviation="{glow}" />
          <feMerge>
            <feMergeNode />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <g filter="url(#glow)">
          {g}
        </g>
      </svg>
    """
    return svg2png(svg)
  except Exception as e:
    with open('build/error.svg', 'w') as f:
      f.write(svg)
    raise e
  

out_path = Path('build/glow/IconBundles')
if not out_path.exists():
  print(f'Initializing output directory {out_path}.')
  Path.mkdir(out_path, parents=True)
  shutil.copyfile('source/Info.plist', Path(out_path.parent, 'Info.plist'))

app_ids = read_app_ids('source/app_ids.csv')

for svgfile in Path.glob('source/limelight_src_*.svg'):
  print(f'Rendering icons in {svgfile}')
  soup = BeautifulSoup(open(svgfile), 'xml').svg
  [icon_g] = soup('g', id='Icons')
  icons = icon_g('g', recursive=False)[::-1]
  for i in range(len(icons)):
    grid = (i%12 + 1, math.floor(i/12) + 1)

    vprint(f'Rendering a:{grid[0]}:{grid[1]} - ', end='')
    try:
      icon, gids = read_svg(icons[i], app_ids)
    except NotImplementedError as e:
      vprint(f'WARNING! Icon marked as unknown. Skipping.')
      continue

    vprint(f'{gids} ({icon["id"]})...', end='')
    png = render_svg(icon, soup.style, grid, glow=20)
    for fname in gids:
      fpath = Path(out_path, f'{fname}-large.png')
      with open(fpath, mode='w+b') as f:
        f.write(png)
        print('.', end='', flush=True)
    vprint()
  print(f'\nFinished rendering {len(icons)} icons.')