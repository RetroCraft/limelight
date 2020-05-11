import gi
gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg

import io

import cairo
from pathlib import Path

def render(g, style, grid, effect=None):
  try:
    coords = (440 + grid[0]*1080 + 90, 440 + grid[1]*1080 + 90) 
    to_render = effect(g) if effect else str(g)
    svg = f"""
      <svg
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        viewBox="{coords[0]} {coords[1]} 900 900"
      >
        {style}{to_render}
      </svg>
    """
    return render_svg(svg)
  except Exception as e:
    with open('error.svg', 'w') as f:
      f.write(svg)
    print('Encountered error. Refer to error.svg.')
    raise e

def render_svg(svg):
  img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 900, 900)
  ctx = cairo.Context(img)

  handle = Rsvg.Handle().new_from_data(svg.encode('utf-8'))
  handle.render_cairo(ctx)
  with io.BytesIO() as stream:
    img.write_to_png(stream)
    return stream.getvalue()
