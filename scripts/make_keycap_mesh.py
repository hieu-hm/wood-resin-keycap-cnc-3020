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


def rect_points(w, d, z):
    hw, hd = w / 2, d / 2
    return [(-hw, -hd, z), (hw, -hd, z), (hw, hd, z), (-hw, hd, z)]


def add_quad(tris, p0, p1, p2, p3):
    tris.append((p0, p1, p2))
    tris.append((p0, p2, p3))


def add_ring_between_rects(tris, outer, inner, reverse=False):
    for i in range(4):
        o0, o1 = outer[i], outer[(i + 1) % 4]
        i0, i1 = inner[i], inner[(i + 1) % 4]
        if reverse:
            add_quad(tris, o0, i0, i1, o1)
        else:
            add_quad(tris, o0, o1, i1, i0)


def cap_top_z(x, y, top_w=12.8, top_d=12.8, height=9.6, dish=0.35):
    rx = abs(x) / (top_w / 2)
    ry = abs(y) / (top_d / 2)
    r = min(1.0, math.sqrt(rx * rx + ry * ry) / math.sqrt(2))
    return height - dish * (1.0 - r * r)


def add_top_grid(tris, n=12, top_w=12.8, top_d=12.8):
    pts = []
    for iy in range(n + 1):
        row = []
        y = -top_d / 2 + top_d * iy / n
        for ix in range(n + 1):
            x = -top_w / 2 + top_w * ix / n
            row.append((x, y, cap_top_z(x, y, top_w, top_d)))
        pts.append(row)
    for iy in range(n):
        for ix in range(n):
            p00 = pts[iy][ix]
            p10 = pts[iy][ix + 1]
            p11 = pts[iy + 1][ix + 1]
            p01 = pts[iy + 1][ix]
            add_quad(tris, p00, p10, p11, p01)


def make_wood_body():
    tris = []

    bottom_w = 18.2
    bottom_d = 18.2
    top_w = 12.8
    top_d = 12.8
    height = 9.6
    wall = 1.25
    top_thick = 1.65
    bottom_z = 0.0
    inner_top_z = height - top_thick

    outer_bottom = rect_points(bottom_w, bottom_d, bottom_z)
    outer_top = [
        (-top_w / 2, -top_d / 2, cap_top_z(-top_w / 2, -top_d / 2)),
        (top_w / 2, -top_d / 2, cap_top_z(top_w / 2, -top_d / 2)),
        (top_w / 2, top_d / 2, cap_top_z(top_w / 2, top_d / 2)),
        (-top_w / 2, top_d / 2, cap_top_z(-top_w / 2, top_d / 2)),
    ]

    # Outer tapered walls.
    for i in range(4):
        add_quad(tris, outer_bottom[i], outer_bottom[(i + 1) % 4], outer_top[(i + 1) % 4], outer_top[i])

    add_top_grid(tris)

    inner_bottom = rect_points(bottom_w - 2 * wall, bottom_d - 2 * wall, bottom_z + 0.25)
    inner_top = rect_points(top_w - 2 * wall, top_d - 2 * wall, inner_top_z)

    # Inner cavity walls, open at bottom.
    for i in range(4):
        add_quad(tris, inner_bottom[(i + 1) % 4], inner_bottom[i], inner_top[i], inner_top[(i + 1) % 4])

    # Underside ceiling around resin insert pocket.
    pocket = rect_points(7.4, 7.4, inner_top_z)
    add_ring_between_rects(tris, inner_top, pocket, reverse=True)

    # Pocket walls for resin insert to locate in wood.
    pocket_bottom = rect_points(7.4, 7.4, inner_top_z - 2.2)
    for i in range(4):
        add_quad(tris, pocket[i], pocket[(i + 1) % 4], pocket_bottom[(i + 1) % 4], pocket_bottom[i])

    # Small bottom lip face between outer and inner bottom.
    add_ring_between_rects(tris, outer_bottom, inner_bottom, reverse=False)
    return tris


def box_tris(cx, cy, z0, sx, sy, sz):
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    z1 = z0 + sz
    v = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]
    faces = [
        (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
    ]
    tris = []
    for a, b, c, d in faces:
        add_quad(tris, v[a], v[b], v[c], v[d])
    return tris


def make_resin_insert():
    tris = []
    # Resin anchor plate sits in a square pocket under the top.
    tris.extend(box_tris(0, 0, 5.75, 7.1, 7.1, 2.05))

    # Material around the Cherry MX female cruciform socket.
    # The open socket is formed by leaving a cross-shaped void at the center.
    z0 = 1.75
    z1 = 5.90
    h = z1 - z0
    outer = 6.0
    slot_len = 4.2
    slot_w = 1.32
    o = outer / 2
    l = slot_len / 2
    s = slot_w / 2
    # Corner masses.
    for cx in (-(o + s) / 2, (o + s) / 2):
        for cy in (-(o + s) / 2, (o + s) / 2):
            tris.extend(box_tris(cx, cy, z0, o - s, o - s, h))
    # End caps for the horizontal and vertical arms of the cross socket.
    tris.extend(box_tris(-(o + l) / 2, 0, z0, o - l, slot_w, h))
    tris.extend(box_tris((o + l) / 2, 0, z0, o - l, slot_w, h))
    tris.extend(box_tris(0, -(o + l) / 2, z0, slot_w, o - l, h))
    tris.extend(box_tris(0, (o + l) / 2, z0, slot_w, o - l, h))
    return tris


def make_combined():
    return make_wood_body() + make_resin_insert()


def write_svg_template():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="220mm" height="160mm" viewBox="-40 -35 80 58">
  <style>
    .cut { fill: none; stroke: #111; stroke-width: 0.25; }
    .pocket { fill: none; stroke: #0a6; stroke-width: 0.25; stroke-dasharray: 1 0.8; }
    .stem { fill: #d33; fill-opacity: 0.18; stroke: #d33; stroke-width: 0.2; }
    .text { font-family: Arial, sans-serif; font-size: 2.2px; fill: #111; }
  </style>
  <text x="-36" y="-30" class="text">Keycap 1u Cherry MX - wood body + resin insert, units mm</text>
  <rect x="-9.1" y="-9.1" width="18.2" height="18.2" class="cut"/>
  <rect x="-6.4" y="-6.4" width="12.8" height="12.8" class="pocket"/>
  <rect x="-3.7" y="-3.7" width="7.4" height="7.4" class="pocket"/>
  <text x="-9.1" y="13" class="text">Bottom 18.2 x 18.2</text>
  <text x="-6.4" y="16" class="text">Top 12.8 x 12.8</text>
  <text x="-3.7" y="19" class="text">Resin pocket 7.4 x 7.4</text>
  <g transform="translate(24,0)">
    <rect x="-2.1" y="-0.66" width="4.2" height="1.32" class="stem"/>
    <rect x="-0.66" y="-2.1" width="1.32" height="4.2" class="stem"/>
    <rect x="-3.55" y="-3.55" width="7.1" height="7.1" class="pocket"/>
    <text x="-8" y="9" class="text">Cherry MX socket reference</text>
    <text x="-8" y="12" class="text">slot 4.2 x 1.32, centered</text>
  </g>
  <g transform="translate(0,31)">
    <path d="M -9.1 0 L -6.4 -9.6 L 6.4 -9.6 L 9.1 0 Z" class="cut"/>
    <path d="M -7.85 -0.25 L -5.15 -7.95 L 5.15 -7.95 L 7.85 -0.25" class="pocket"/>
    <text x="-9.1" y="5" class="text">Side profile: height 9.6, wall 1.25, top thickness 1.65</text>
  </g>
</svg>
"""
    DRAWINGS.mkdir(parents=True, exist_ok=True)
    (DRAWINGS / "keycap_1u_cherry_mx_layout.svg").write_text(svg, encoding="ascii")


def write_readme():
    text = """# Keycap 1u Cherry MX - wood body + resin stem insert

Units: millimeters.

Generated files:
- `keycap_1u_cherry_mx_wood_body.stl`: wooden outer keycap shell.
- `keycap_1u_cherry_mx_resin_insert.stl`: resin insert with underside Cherry MX female socket.
- `keycap_1u_cherry_mx_wood_resin_assembly.stl`: combined preview assembly.
- `keycap_1u_cherry_mx_layout.svg`: 2D dimension reference for bottom/top/pocket/stem.

Nominal dimensions:
- 1u outside bottom: 18.2 x 18.2 mm.
- Top face: 12.8 x 12.8 mm.
- Height: 9.6 mm.
- Wall thickness: 1.25 mm.
- Top thickness: 1.65 mm.
- Resin pocket: 7.4 x 7.4 x 2.2 mm under the top.
- Cherry MX female socket: centered, about 4.2 x 1.32 mm each slot, depth about 4.15 mm.

Manufacturing notes:
- This is a practical starting model, not an official Cherry MX mechanical drawing.
- For CNC wood, leave 0.15-0.30 mm extra clearance around the resin insert depending on wood movement and resin shrinkage.
- Do a fit test before making a full set. Cherry-compatible switches and printers/CNC postprocessors vary.
- For resin casting, machine/print the wood body first, seal the wood, cast resin into the 7.4 mm pocket, then finish-machine the Cherry MX socket in the resin if your casting process cannot hold that detail.
- For a production STEP file, remodel this parametric design in Fusion 360/SolidWorks/FreeCAD from the dimensions above and then toolpath from STEP.
"""
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "README_keycap_1u_cherry_mx_wood_resin.md").write_text(text, encoding="utf-8")


def main():
    MODELS.mkdir(parents=True, exist_ok=True)
    write_ascii_stl(MODELS / "keycap_1u_cherry_mx_wood_body.stl", "wood_body", make_wood_body())
    write_ascii_stl(MODELS / "keycap_1u_cherry_mx_resin_insert.stl", "resin_insert", make_resin_insert())
    write_ascii_stl(MODELS / "keycap_1u_cherry_mx_wood_resin_assembly.stl", "wood_resin_assembly", make_combined())
    write_svg_template()
    write_readme()


if __name__ == "__main__":
    main()
