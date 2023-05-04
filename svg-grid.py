#!/usr/bin/env python
import xml.etree.ElementTree as ET
import argparse
import sys

p = argparse.ArgumentParser(description="Converts CSV file into SVG grid.")

p.add_argument("-d", "--delimiter", default=",", help="character separating input fields")
p.add_argument("--margin", type=float, default=10, help="margin around SVG grid in px")
p.add_argument("--line-width", type=float, default=2, help="width of grid lines in px")
p.add_argument("--line-color", default="black", help="color of grid lines")
p.add_argument("--cell-width", type=float,  default=50, help="width of table cells in px")
p.add_argument("--cell-height", type=float, default=50, help="height of table cells in px")
p.add_argument("--font-size", default="30px")
p.add_argument("--font-family", default="monospace")
p.add_argument("filename", type=argparse.FileType(), default=sys.stdin, nargs="?", help="CSV file. Defaults to standard input")
p.add_argument("-o", "--output", type=argparse.FileType('wb'), default=sys.stdout, help="Output file. Defaults to standard output", metavar="OUT_FILE")

args = p.parse_args()

margin = args.margin
cw = args.cell_width
ch = args.cell_height
lw = args.line_width

# for text placement on grid:
x0 = margin + lw + cw*0.13
y0 = margin + lw + ch*0.7   # text baseline
Δx = cw + lw
Δy = ch + lw

ET.register_namespace("", "http://www.w3.org/2000/svg")

g = ET.Element("g", attrib={"font-size": args.font_size, "font-family": args.font_family})

maxj = 0
for i, line in enumerate(args.filename):
    for j, field in enumerate(line.split(args.delimiter)):
        maxj = max(maxj, j)
        e = ET.SubElement(g, "text", x=str(x0 + j*Δx), y=str(y0 + i*Δy))
        e.text = field.strip()

rows = i + 1     # number of lines in file
cols = maxj + 1  # max number of columns

gridwidth = Δx*cols + lw
gridheight = Δy*rows + lw

svg = ET.XML(f'''
<svg
    width="{2*margin + gridwidth}"
    height="{2*margin + gridheight}"
    version="1.1">
  <defs>
    <pattern
       id="grid"
       x="{margin}"
       y="{margin}"
       width="{Δx}"
       height="{Δy}"
       patternUnits="userSpaceOnUse">
      <path
         fill="none"
         stroke="{args.line_color}"
         stroke-width="{2*lw}"
         d="M {Δx} 0 L 0 0 0 {Δy}" />
    </pattern>
  </defs>
  <rect
     width="{gridwidth}"
     height="{gridheight}"
     fill="url(#grid)"
     x="{margin}"
     y="{margin}" />
</svg>
''')
svg.set('xmlns', "http://www.w3.org/2000/svg")
svg.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
svg.append(g)

tree = ET.ElementTree(svg)
ET.indent(tree)
tree.write(args.output, xml_declaration=True, encoding="UTF-8")
