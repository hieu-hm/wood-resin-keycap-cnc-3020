import math
import struct
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
DOCS = ROOT / "docs"

SOURCE = Path(r"C:\Users\ADMIN\Downloads\1x1 R1.stl")
OUT_STL = MODELS / "keycap_1u_r1_sample_exact_square_recess.stl"
OUT_DOC = DOCS / "README_keycap_1u_r1_sample_exact_square_recess.md"
OUT_BOTTOM = ROOT / "drawings" / "keycap_1u_r1_sample_exact_square_recess_bottom.png"
OUT_SIDE = ROOT / "drawings" / "keycap_1u_r1_sample_exact_square_recess_side.png"
OUT_BOTTOM_CLEAN = ROOT / "drawings" / "keycap_1u_r1_sample_exact_square_recess_bottom_clean.png"


SQUARE_HALF = 2.80
RECESS_TOP_Y = 3.90
BOTTOM_Y = 0.0


def read_binary_stl(path: Path):
    data = path.read_bytes()
    tri_count = struct.unpack_from("<I", data, 80)[0]
    expected = 84 + tri_count * 50
    if len(data) != expected:
        raise ValueError("Only binary STL is supported for this script.")
    header = data[:80]
    triangles = []
    offset = 84
    for _ in range(tri_count):
        normal = struct.unpack_from("<fff", data, offset)
        offset += 12
        tri = []
        for _ in range(3):
            tri.append(struct.unpack_from("<fff", data, offset))
            offset += 12
        attr = struct.unpack_from("<H", data, offset)[0]
        offset += 2
        triangles.append((normal, tuple(tri), attr))
    return header, triangles


def write_binary_stl(path: Path, header: bytes, triangles):
    header = (header[:80] + b" " * 80)[:80]
    with open(path, "wb") as f:
        f.write(header)
        f.write(struct.pack("<I", len(triangles)))
        for _, tri, attr in triangles:
            n = tri_normal(*tri)
            f.write(struct.pack("<fff", *n))
            for v in tri:
                f.write(struct.pack("<fff", *v))
            f.write(struct.pack("<H", attr))


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


def centroid(tri):
    return (
        (tri[0][0] + tri[1][0] + tri[2][0]) / 3.0,
        (tri[0][1] + tri[1][1] + tri[2][1]) / 3.0,
        (tri[0][2] + tri[1][2] + tri[2][2]) / 3.0,
    )


def tri_in_stem_region(tri):
    # Remove any triangle that occupies the square cavity volume or touches its
    # replacement boundary. This is more aggressive than centroid-only removal
    # and prevents leftover internal geometry from surviving inside the recess.
    xs = [v[0] for v in tri]
    ys = [v[1] for v in tri]
    zs = [v[2] for v in tri]
    if max(ys) < BOTTOM_Y - 0.05 or min(ys) > RECESS_TOP_Y + 0.25:
        return False
    if max(xs) < -SQUARE_HALF - 0.05 or min(xs) > SQUARE_HALF + 0.05:
        return False
    if max(zs) < -SQUARE_HALF - 0.05 or min(zs) > SQUARE_HALF + 0.05:
        return False
    return True


def add_quad(tris, p0, p1, p2, p3, attr=0):
    tris.append(((0.0, 0.0, 0.0), (p0, p1, p2), attr))
    tris.append(((0.0, 0.0, 0.0), (p0, p2, p3), attr))


def build_square_recess(attr=0):
    tris = []
    s = SQUARE_HALF
    b = BOTTOM_Y
    t = RECESS_TOP_Y
    bottom = [(-s, b, -s), (s, b, -s), (s, b, s), (-s, b, s)]
    top = [(-s, t, -s), (s, t, -s), (s, t, s), (-s, t, s)]
    # Top of recess.
    add_quad(tris, top[0], top[3], top[2], top[1], attr=attr)
    # Side walls.
    add_quad(tris, bottom[1], bottom[0], top[0], top[1], attr=attr)
    add_quad(tris, bottom[2], bottom[1], top[1], top[2], attr=attr)
    add_quad(tris, bottom[3], bottom[2], top[2], top[3], attr=attr)
    add_quad(tris, bottom[0], bottom[3], top[3], top[0], attr=attr)
    return tris


def render_projection(triangles, axes, out_path: Path, size=(1200, 1200), margin=40, outline=True):
    ax0, ax1, depth_axis = axes
    pts = [v for _, tri, _ in triangles for v in tri]
    min0 = min(v[ax0] for v in pts)
    max0 = max(v[ax0] for v in pts)
    min1 = min(v[ax1] for v in pts)
    max1 = max(v[ax1] for v in pts)
    span0 = max0 - min0
    span1 = max1 - min1
    scale = min((size[0] - 2 * margin) / span0, (size[1] - 2 * margin) / span1)

    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)

    def proj(v):
        x = margin + (v[ax0] - min0) * scale
        y = size[1] - (margin + (v[ax1] - min1) * scale)
        return (x, y)

    ordered = sorted(
        triangles,
        key=lambda item: sum(v[depth_axis] for v in item[1]) / 3.0
    )
    for _, tri, _ in ordered:
        poly = [proj(v) for v in tri]
        n = tri_normal(*tri)
        shade = int(170 + 70 * abs(n[depth_axis]))
        draw.polygon(poly, fill=(shade, shade, shade), outline=(70, 70, 70) if outline else None)
    img.save(out_path)


def main():
    MODELS.mkdir(parents=True, exist_ok=True)
    (ROOT / "drawings").mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    header, triangles = read_binary_stl(SOURCE)
    kept = [item for item in triangles if not tri_in_stem_region(item[1])]
    attr = triangles[0][2] if triangles else 0
    patched = kept + build_square_recess(attr=attr)

    write_binary_stl(OUT_STL, b"sample_r1_square_recess", patched)

    render_projection(patched, axes=(0, 2, 1), out_path=OUT_BOTTOM)
    render_projection(patched, axes=(0, 1, 2), out_path=OUT_SIDE)
    render_projection(patched, axes=(0, 2, 1), out_path=OUT_BOTTOM_CLEAN, outline=False)

    OUT_DOC.write_text(
        "# Keycap 1u R1 from sample - square recess bottom\n\n"
        "This file is edited from the user's sample STL `1x1 R1.stl`.\n\n"
        "Change made:\n"
        "- removed the central Cherry-style cross/stem region on the underside\n"
        "- replaced it with a square recessed pocket\n\n"
        "Patch parameters used:\n"
        f"- square half-size: {SQUARE_HALF} mm\n"
        f"- square size: {SQUARE_HALF * 2:.2f} mm\n"
        f"- recess depth from bottom: {RECESS_TOP_Y:.2f} mm\n"
        "\n"
        "Output files:\n"
        f"- `{OUT_STL.name}`\n"
        f"- `{OUT_BOTTOM.name}`\n"
        f"- `{OUT_BOTTOM_CLEAN.name}`\n"
        f"- `{OUT_SIDE.name}`\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
