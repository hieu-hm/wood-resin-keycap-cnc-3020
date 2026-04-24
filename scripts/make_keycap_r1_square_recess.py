import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
DRAWINGS = ROOT / "drawings"
DOCS = ROOT / "docs"


def tri_normal(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (nx / length, ny / length, nz / length)


def write_ascii_stl(path, name, triangles):
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(f"solid {name}\n")
        for a, b, c in triangles:
            nx, ny, nz = tri_normal(a, b, c)
            f.write(f"  facet normal {nx:.8f} {ny:.8f} {nz:.8f}\n")
            f.write("    outer loop\n")
            for p in (a, b, c):
                f.write(f"      vertex {p[0]:.5f} {p[1]:.5f} {p[2]:.5f}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write(f"endsolid {name}\n")


def add_quad(tris, p0, p1, p2, p3):
    tris.append((p0, p1, p2))
    tris.append((p0, p2, p3))


def rect_points(w, d, z, y_offset=0.0):
    hw, hd = w / 2, d / 2
    return [
        (-hw, y_offset - hd, z),
        (hw, y_offset - hd, z),
        (hw, y_offset + hd, z),
        (-hw, y_offset + hd, z),
    ]


def add_ring_between_rects(tris, outer, inner, reverse=False):
    for i in range(4):
        o0, o1 = outer[i], outer[(i + 1) % 4]
        i0, i1 = inner[i], inner[(i + 1) % 4]
        if reverse:
            add_quad(tris, o0, i0, i1, o1)
        else:
            add_quad(tris, o0, o1, i1, i0)


def top_surface_z(x, y, top_w=13.0, top_d=13.0, top_offset_y=0.8):
    rx = x / (top_w / 2)
    ry = (y - top_offset_y) / (top_d / 2)
    radial = min(1.0, math.sqrt(rx * rx + ry * ry) / math.sqrt(2))
    slope = 0.95 * ry
    dish = 0.30 * (1.0 - radial * radial)
    cross_curve = 0.08 * (1.0 - min(1.0, rx * rx))
    return 8.95 + slope - dish + cross_curve


def add_top_grid(tris, n=18, top_w=13.0, top_d=13.0, top_offset_y=0.8):
    pts = []
    for iy in range(n + 1):
        row = []
        y = top_offset_y - top_d / 2 + top_d * iy / n
        for ix in range(n + 1):
            x = -top_w / 2 + top_w * ix / n
            row.append((x, y, top_surface_z(x, y, top_w, top_d, top_offset_y)))
        pts.append(row)
    for iy in range(n):
        for ix in range(n):
            p00 = pts[iy][ix]
            p10 = pts[iy][ix + 1]
            p11 = pts[iy + 1][ix + 1]
            p01 = pts[iy + 1][ix]
            add_quad(tris, p00, p10, p11, p01)


def make_keycap():
    tris = []

    bottom_w = 18.0
    bottom_d = 18.0
    top_w = 13.0
    top_d = 13.0
    top_offset_y = 0.8
    recess_w = 7.4
    recess_d = 7.4
    recess_depth = 5.0

    outer_bottom = rect_points(bottom_w, bottom_d, 0.0)
    outer_top = [
        (-top_w / 2, top_offset_y - top_d / 2, top_surface_z(-top_w / 2, top_offset_y - top_d / 2)),
        (top_w / 2, top_offset_y - top_d / 2, top_surface_z(top_w / 2, top_offset_y - top_d / 2)),
        (top_w / 2, top_offset_y + top_d / 2, top_surface_z(top_w / 2, top_offset_y + top_d / 2)),
        (-top_w / 2, top_offset_y + top_d / 2, top_surface_z(-top_w / 2, top_offset_y + top_d / 2)),
    ]

    for i in range(4):
        add_quad(tris, outer_bottom[i], outer_bottom[(i + 1) % 4], outer_top[(i + 1) % 4], outer_top[i])

    add_top_grid(tris, top_w=top_w, top_d=top_d, top_offset_y=top_offset_y)

    recess_bottom = rect_points(recess_w, recess_d, 0.0)
    recess_roof = rect_points(recess_w, recess_d, recess_depth)

    add_ring_between_rects(tris, outer_bottom, recess_bottom, reverse=False)

    for i in range(4):
        add_quad(tris, recess_bottom[(i + 1) % 4], recess_bottom[i], recess_roof[i], recess_roof[(i + 1) % 4])

    add_quad(tris, recess_roof[0], recess_roof[1], recess_roof[2], recess_roof[3])
    return tris


def write_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="220mm" height="160mm" viewBox="-42 -38 84 66">
  <style>
    .cut { fill: none; stroke: #111; stroke-width: 0.25; }
    .pocket { fill: rgba(30, 120, 255, 0.12); stroke: #1565c0; stroke-width: 0.25; }
    .guide { fill: none; stroke: #888; stroke-width: 0.18; stroke-dasharray: 1 0.8; }
    .text { font-family: Arial, sans-serif; font-size: 2.2px; fill: #111; }
  </style>
  <text x="-38" y="-33" class="text">1u R1 style keycap, solid body, square bottom recess only, units mm</text>
  <rect x="-9" y="-9" width="18" height="18" class="cut"/>
  <rect x="-3.7" y="-3.7" width="7.4" height="7.4" class="pocket"/>
  <rect x="-6.5" y="-5.7" width="13" height="13" class="guide"/>
  <text x="-9" y="13" class="text">Bottom 18.0 x 18.0</text>
  <text x="-6.5" y="16" class="text">Top reference 13.0 x 13.0, shifted +0.8 in Y</text>
  <text x="-3.7" y="19" class="text">Bottom recess 7.4 x 7.4 x 5.0 deep</text>
  <g transform="translate(0,33)">
    <path d="M -9 0 L -6.5 -0.5 L -6.5 -8.0 L 6.5 -9.8 L 6.5 -0.5 L 9 0 Z" class="cut"/>
    <rect x="-3.7" y="-5" width="7.4" height="5" class="pocket"/>
    <text x="-10" y="5" class="text">Side idea: R1 top slope, total height about 9.8</text>
  </g>
</svg>
"""
    DRAWINGS.mkdir(parents=True, exist_ok=True)
    (DRAWINGS / "keycap_1u_r1_square_recess_layout.svg").write_text(svg, encoding="ascii")


def write_doc():
    text = """# Keycap 1u R1 style - square recessed bottom

Units: millimeters.

This model is a clean remake inspired by the reference `1x1 R1.stl`, but simplified underneath:
- no Cherry MX cross
- no resin stem geometry
- underside uses only a square recessed pocket

Generated files:
- `models/keycap_1u_r1_square_recess.stl`
- `drawings/keycap_1u_r1_square_recess_layout.svg`

Nominal dimensions:
- Bottom footprint: 18.0 x 18.0 mm
- Overall height: about 9.8 mm
- Top reference area: 13.0 x 13.0 mm
- Top reference offset: +0.8 mm in Y
- Bottom square recess: 7.4 x 7.4 x 5.0 mm deep

Notes:
- Model uses standard CAD orientation with Z up.
- Body is solid except for the square bottom recess.
- Top surface has an R1-style front/back slope plus a light dish.
- If you want the bottom recess larger, deeper, or offset, edit the values in `scripts/make_keycap_r1_square_recess.py`.
"""
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "README_keycap_1u_r1_square_recess.md").write_text(text, encoding="utf-8")


def main():
    MODELS.mkdir(parents=True, exist_ok=True)
    write_ascii_stl(MODELS / "keycap_1u_r1_square_recess.stl", "keycap_1u_r1_square_recess", make_keycap())
    write_svg()
    write_doc()


if __name__ == "__main__":
    main()
