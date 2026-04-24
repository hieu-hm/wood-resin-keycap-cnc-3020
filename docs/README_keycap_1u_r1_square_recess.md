# Keycap 1u R1 style - square recessed bottom

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
