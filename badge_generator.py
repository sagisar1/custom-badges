# ------------------------------------------------------------------------------
# This script attempts to create badges with your prefered SVG logo, in a way that results
# quite similar to shields.io. The script creats a self contained svg image that you can use then
# in your github README.md or other places.
# Colors can be specified in their name (white,red) or as hex colors codes (for example: #333 or #2927A0)
# Default text color is white (see TEXT_COLOR constant below), but you can change it as you want.
# [*] Specifying white text color with white badge will result in white badge and black text color.
# ------------------------------------------------------------------------------
import requests
from lxml import etree


# Configurable options - change options according to your preference:
LOGO_URL = "http://example.com/example.svg" # Change this to a URL of your SVG logo
BADGE_TEXT = "text-on-badge"
BADGE_COLOR = "black" 
TEXT_COLOR = "white"  
TEXT_BACKGROUND_COLOR = "#010101" # default background text color is black


# Font and badge metrics
FONT_SIZE = 11
CHAR_WIDTH = 7  # Approximate width per character, adjust as needed
LOGO_SIZE = 14
BADGE_HEIGHT = 20
PADDING = 2
LOGO_LEFT = 5

def calc_badge_width(text):
    # logo + left pad + text + right pad
    return LOGO_LEFT + LOGO_SIZE + PADDING + len(text) * CHAR_WIDTH + PADDING

def fetch_svg_logo(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_logo_bbox(svg_data):
    # Get viewBox or width/height from SVG root
    tree = etree.fromstring(svg_data.encode())
    vb = tree.attrib.get('viewBox')
    if vb:
        vb = [float(x) for x in vb.strip().split()]
        x, y, w, h = vb
    else:
        w = float(tree.attrib.get('width', LOGO_SIZE))
        h = float(tree.attrib.get('height', LOGO_SIZE))
        x = y = 0
    return x, y, w, h, tree

def extract_logo_inner(tree):
    # Returns inner XML of SVG root (excluding <svg> itself)
    return ''.join([etree.tostring(child).decode() for child in tree]) #if child.tag != '{http://www.w3.org/2000/svg}defs'])

def make_badge(logo_inner, logo_bbox, text, badge_color,text_color,background_text_color,width):
    if (badge_color == "white" or badge_color == "#fff" or badge_color == "#ffffff") and (text_color == "white" or text_color == "#fff" or text_color == "#ffffff") :
        text_color = "#333" #dark gray color
        background_text_color="#ccc" #bright gray background color
    
    x, y, w, h, _ = logo_bbox
    # Compute scale to fit logo in LOGO_SIZE
    scale = LOGO_SIZE / max(w, h)
    # Center logo vertically in badge
    logo_y = (BADGE_HEIGHT - LOGO_SIZE) // 2
    # Compose SVG
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{BADGE_HEIGHT}" role="img" aria-label="{text}">
  <title>{text}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{width}" height="{BADGE_HEIGHT}" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{width}" height="{BADGE_HEIGHT}" fill="{badge_color}"/>
    <rect width="{width}" height="{BADGE_HEIGHT}" fill="url(#s)"/>
  </g>
  <g id="logo" transform="translate({LOGO_LEFT},{logo_y}) scale({scale}) translate({-x},{-y})">
    {logo_inner}
  </g>
  <text aria-hidden="true" x="{LOGO_LEFT + LOGO_SIZE + PADDING + (len(text)*CHAR_WIDTH)//2}" y="15" fill="{background_text_color}" fill-opacity=".3"
        font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="{FONT_SIZE}"
        text-anchor="middle">{text}</text>
  <text x="{LOGO_LEFT + LOGO_SIZE + PADDING + (len(text)*CHAR_WIDTH)//2}" y="14" fill="{text_color}"
        font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="{FONT_SIZE}"
        text-anchor="middle">{text}</text>
</svg>'''

def main():
    svg_logo = fetch_svg_logo(LOGO_URL)
    logo_bbox = parse_logo_bbox(svg_logo)
    logo_inner = extract_logo_inner(logo_bbox[4])
    width = calc_badge_width(BADGE_TEXT)
    badge_svg = make_badge(logo_inner, logo_bbox, BADGE_TEXT, BADGE_COLOR,TEXT_COLOR,TEXT_BACKGROUND_COLOR,width)
    with open(f"{BADGE_TEXT}-badge.svg", "w") as f:
        f.write(badge_svg)
    print(f"Badge generated: {BADGE_TEXT}-badge.svg (width: {width})")

if __name__ == "__main__":
    main()