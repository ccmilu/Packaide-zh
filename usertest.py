# Example usage of Packaide
import packaide

# Shapes are provided in SVG format
shapes = """
<svg viewBox="0 0 432.13 593.04">
  <rect width="100" height="50" />
  <rect width="50" height="100" />
  <ellipse rx="20" ry="20" />
</svg>
"""

# The target sheet / material is also represented as an SVG 
# document. Shapes given on the sheet are interpreted as
# holes that must be avoided when placing new parts. In this
# case, a square in the upper-left-hand corner.
sheet = """
<svg width="300" height="300" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="100" height="100" />
</svg>
"""

# Attempts to pack as many of the parts as possible.
result, placed, fails = packaide.pack(
  [sheet],                  # A list of sheets (SVG documents)
  shapes,                   # An SVG document containing the parts
  tolerance = 2.5,          # Discretization tolerance
  offset = 5,               # The offset distance around each shape (dilation)
  partial_solution = True,  # Whether to return a partial solution
  rotations = 1,            # The number of rotations of parts to try
  persist = True            # Cache results to speed up next run
)

# If partial_solution was False, then either every part is placed or none
# are. Otherwise, as many as possible are placed. placed and fails denote
# the number of parts that could be and could not be placed respectively
print("{} parts were placed. {} parts could not fit on the sheets".format(placed, fails))

# The results are given by a list of pairs (i, out), where
# i is the index of the sheet on which shapes were packed, and
# out is an SVG representation of the parts that are to be
# placed on that sheet.
for i, out in result:
  with open('result_sheet_{}.svg'.format(i), 'w') as f_out:
    f_out.write(out)