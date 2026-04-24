# Wood Resin Keycap CNC 3020

Project for a 1u Cherry MX compatible keycap with a CNC-machined wood body and a resin stem/insert.

## Files

- `models/keycap_1u_cherry_mx_wood_body.stl` - wood body model for CAM.
- `models/keycap_1u_cherry_mx_resin_insert.stl` - square resin insert/pour block with underside Cherry MX female socket.
- `models/keycap_1u_cherry_mx_wood_resin_assembly.stl` - combined preview assembly.
- `models/keycap_1u_r1_square_recess.stl` - R1-style 1u keycap with only a square bottom recess.
- `drawings/keycap_1u_cherry_mx_layout.svg` - 2D dimension reference.
- `drawings/keycap_1u_r1_square_recess_layout.svg` - 2D reference for the square-recess variant.
- `cam/CNC_3020_PLUS_keycap_job_sheet.md` - machining notes for CNC 3020 Plus.
- `docs/README_keycap_1u_cherry_mx_wood_resin.md` - dimensions and manufacturing notes.
- `docs/README_keycap_1u_r1_square_recess.md` - dimensions for the square-recess variant.
- `scripts/make_keycap_mesh.py` - regenerates the STL/SVG/docs files.
- `scripts/make_keycap_r1_square_recess.py` - generates the R1-style square-recess variant.

## Nominal Dimensions

- Bottom: 18.2 x 18.2 mm.
- Top face: 12.8 x 12.8 mm.
- Height: 9.6 mm.
- Wall thickness: 1.25 mm.
- Top thickness: 1.65 mm.
- Resin pour pocket: 7.4 x 7.4 x 5.0 mm.
- Cherry MX socket: about 4.2 x 1.32 mm slots, centered, with about 5.0 mm resin depth available.

## Suggested Workflow

1. Open `models/keycap_1u_cherry_mx_wood_body.stl` in CAM.
2. Set units to millimeters.
3. Set origin at the keycap center, with Z zero on top of stock.
4. Machine the wood body and resin pocket.
5. Seal the wood, cast resin into the 7.4 x 7.4 x 5.0 mm square pocket or install the matching resin insert.
6. Machine/test the Cherry MX socket in resin.
7. Test fit on one switch before making a full set.

## CNC 3020 Plus Notes

Start from `cam/CNC_3020_PLUS_keycap_job_sheet.md`. Choose the postprocessor for your controller:

- GRBL/Candle: GRBL post, usually `.nc`.
- Mach3: Mach3 mill post, usually `.tap` or `.nc`.
- Offline controller: check the accepted extension before posting.

Run a CAM simulation and an air-cut before cutting the real blank.

## Regenerate Files

From the project root:

```powershell
python .\scripts\make_keycap_mesh.py
```

The script writes outputs back into `models/`, `drawings/`, and `docs/`.
