import math

def glow(radius=40):
  """Overlay a Gaussian blur with given radius (default 40)"""
  stdDev = math.floor(radius/2)
  return lambda g: f"""
    <filter id="glow">
      <feGaussianBlur stdDeviation="{stdDev}" />
      <feMerge>
        <feMergeNode />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <g filter="url(#glow)">
      {g}
    </g>
  """
