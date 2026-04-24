import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
DRAWINGS = ROOT / "drawings"
DOCS = ROOT / "docs"

OUT_STL = MODELS / "keycap_1u_hollow_bottom_no_stem.stl"
OUT_BOTTOM = DRAWINGS / "keycap_1u_hollow_bottom_no_stem_bottom.png"
OUT_BOTTOM_CLEAN = DRAWINGS / "keycap_1u_hollow_bottom_no_stem_bottom_clean.png"
OUT_SIDE = DRAWINGS / "keycap_1u_hollow_bottom_no_stem_side.png"
OUT_DOC = DOCS / "README_keycap_1u_hollow_bottom_no_stem.md"


POINTS = 96


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


def superellipse_loop(width, depth, z_func, y_offset=0.0, exponent=5.0, count=POINTS):
    pts = []
    a = width / 2.0
    b = depth / 2.0
    for i in range(count):
        t = 2.0 * math.pi * i / count
        ct = math.cos(t)
        st = math.sin(t)
        x = a * math.copysign(abs(ct) ** (2.0 / exponent), ct)
        y = y_offset + b * math.copysign(abs(st) ** (2.0 / exponent), st)
        pts.append((x, y, z_func(x, y)))
    return pts


def add_quad(tris, p0, p1, p2, p3):
    tris.append((p0, p1, p2))
    tris.append((p0, p2, p3))


def add_loop_bridge(tris, lower, upper, reverse=False):
    count = len(lower)
    for i in range(count):
        j = (i + 1) % count
        if reverse:
            add_quad(tris, lower[i], upper[i], upper[j], lower[j])
        else:
            add_quad(tris, lower[i], lower[j], upper[j], upper[i])


def top_z(x, y):
    # R1-like top: slight front/back slope plus a shallow finger dish.
    rx = x / 6.6
    ry = (y - 0.65) / 6.6
    radial = min(1.0, math.sqrt(rx * rx + ry * ry) / math.sqrt(2.0))
    slope = 0.72 * ry
    dish = 0.30 * (1.0 - radial * radial)
    return 9.15 + slope - dish


def roof_z(x, y):
    # Underside of the top shell. This is the visible ceiling inside the hollow keycap.
    return top_z(x, y) - 1.65


def add_filled_superellipse_surface(tris, width, depth, z_func, y_offset=0.0, exponent=5.0, reverse=False):
    rings = []
    for s in (0.0, 0.22, 0.42, 0.62, 0.80, 1.0):
        if s == 0.0:
            rings.append([(0.0, y_offset, z_func(0.0, y_offset))] * POINTS)
        else:
            rings.append(superellipse_loop(width * s, depth * s, z_func, y_offset, exponent))

    for r in range(len(rings) - 1):
        inner = rings[r]
        outer = rings[r + 1]
        for i in range(POINTS):
            j = (i + 1) % POINTS
            if r == 0:
                tri = (inner[i], outer[j], outer[i]) if reverse else (inner[i], outer[i], outer[j])
                tris.append(tri)
            elif reverse:
                add_quad(tris, inner[i], outer[i], outer[j], inner[j])
            else:
                add_quad(tris, inner[i], inner[j], outer[j], outer[i])


def make_keycap():
    tris = []

    # 1u keycap body dimensions.
    outer_bottom_w = 18.0
    outer_bottom_d = 18.0
    outer_top_w = 13.2
    outer_top_d = 13.2
    top_offset_y = 0.65

    # Hollow underside, no stem.
    inner_bottom_w = 14.8
    inner_bottom_d = 14.8
    inner_roof_w = 14.0
    inner_roof_d = 14.0

    outer_bottom = superellipse_loop(outer_bottom_w, outer_bottom_d, lambda _x, _y: 0.0, exponent=5.8)
    outer_top = superellipse_loop(outer_top_w, outer_top_d, top_z, y_offset=top_offset_y, exponent=5.0)
    inner_bottom = superellipse_loop(inner_bottom_w, inner_bottom_d, lambda _x, _y: 0.0, exponent=5.0)
    inner_roof = superellipse_loop(inner_roof_w, inner_roof_d, roof_z, y_offset=top_offset_y * 0.15, exponent=4.8)

    # Outer tapered side wall.
    add_loop_bridge(tris, outer_bottom, outer_top)

    # Top shell.
    add_filled_superellipse_surface(tris, outer_top_w, outer_top_d, top_z, y_offset=top_offset_y, exponent=5.0)

    # Bottom rim between outside and hollow opening.
    add_loop_bridge(tris, outer_bottom, inner_bottom, reverse=True)

    # Hollow inside walls. This is the empty cavity seen from the bottom.
    add_loop_bridge(tris, inner_bottom, inner_roof, reverse=True)

    # Smooth ceiling of the hollow cavity.
    add_filled_superellipse_surface(tris, inner_roof_w, inner_roof_d, roof_z, y_offset=top_offset_y * 0.15, exponent=4.8, reverse=True)

    return tris


def render_projection(triangles, axes, out_path, size=(1200, 1200), margin=45, outline=True):
    ax0, ax1, depth_axis = axes
    pts = [v for tri in triangles for v in tri]
    min0 = min(v[ax0] for v in pts)
    max0 = max(v[ax0] for v in pts)
    min1 = min(v[ax1] for v in pts)
    max1 = max(v[ax1] for v in pts)
    span0 = max0 - min0
    span1 = max1 - min1
    scale = min((size[0] - 2 * margin) / span0, (size[1] - 2 * margin) / span1)

    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)

    def project(v):
        px = margin + (v[ax0] - min0) * scale
        py = size[1] - (margin + (v[ax1] - min1) * scale)
        return (px, py)

    ordered = sorted(triangles, key=lambda tri: sum(v[depth_axis] for v in tri) / 3.0)
    for tri in ordered:
        normal = tri_normal(*tri)
        shade = int(160 + 80 * abs(normal[depth_axis]))
        draw.polygon([project(v) for v in tri], fill=(shade, shade, shade), outline=(60, 60, 60) if outline else None)
    img.save(out_path)


def write_doc():
    OUT_DOC.write_text(
        "# Keycap 1u hollow bottom, no stem\n\n"
        "Clean model drawn from scratch for CNC/mesh preview.\n\n"
        "Geometry:\n"
        "- 1u outside bottom: 18.0 x 18.0 mm\n"
        "- Overall height: about 9.6 mm\n"
        "- Top reference: about 13.2 x 13.2 mm\n"
        "- Bottom opening: about 14.8 x 14.8 mm\n"
        "- Wall/rim thickness at bottom: about 1.6 mm\n"
        "- Inner wall is near-vertical so the hollow roof matches the cavity cleanly.\n"
        "- Underside is fully hollow and contains no Cherry MX stem, cross, post, bridge, or internal support.\n\n"
        "Output:\n"
        f"- `{OUT_STL.name}`\n"
        f"- `{OUT_BOTTOM.name}`\n"
        f"- `{OUT_BOTTOM_CLEAN.name}`\n"
        f"- `{OUT_SIDE.name}`\n",
        encoding="utf-8",
    )


def main():
    MODELS.mkdir(parents=True, exist_ok=True)
    DRAWINGS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    tris = make_keycap()
    write_ascii_stl(OUT_STL, "keycap_1u_hollow_bottom_no_stem", tris)
    render_projection(tris, axes=(0, 1, 2), out_path=OUT_BOTTOM, outline=True)
    render_projection(tris, axes=(0, 1, 2), out_path=OUT_BOTTOM_CLEAN, outline=False)
    render_projection(tris, axes=(0, 2, 1), out_path=OUT_SIDE, outline=True)
    write_doc()


if __name__ == "__main__":
    main()
