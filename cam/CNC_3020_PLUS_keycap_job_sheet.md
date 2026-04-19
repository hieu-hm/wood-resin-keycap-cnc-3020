# CNC 3020 Plus job sheet - 1u Cherry MX wood + resin keycap

Units: millimeters.

Use these source files:
- Wood body CAM: `keycap_1u_cherry_mx_wood_body.stl`
- Resin insert CAM/test: `keycap_1u_cherry_mx_resin_insert.stl`
- Visual assembly only: `keycap_1u_cherry_mx_wood_resin_assembly.stl`
- 2D dimension reference: `keycap_1u_cherry_mx_layout.svg`

## Machine assumptions

- Machine: CNC 3020 Plus, 3-axis router.
- Work envelope is enough for one keycap.
- Controller can run standard G-code from CAM, commonly `.nc` or `.tap`.
- Verify whether your controller is GRBL/Candle, Mach3, or offline controller before posting G-code.

Do not run unverified G-code directly. First simulate in CAM, then air-cut above the stock.

## Suggested stock

For one keycap:
- Wood blank: 25 x 25 x 13 mm minimum.
- Safer blank: 30 x 30 x 15 mm.
- Final keycap body: about 18.2 x 18.2 x 9.6 mm.

Clamp the blank on a spoilboard. Leave at least 3 mm margin around the keycap for tabs or double-sided tape.

## Work coordinate setup

Recommended origin:
- X0/Y0: center of keycap.
- Z0: top of stock.

This matches the generated STL centerline and makes flipping/indexing easier.

## Tooling

For wood body:
- Roughing: 2.0 mm flat end mill.
- Finishing outer/top surface: 1.0 mm ball nose or 1.0 mm flat end mill.
- Inner cavity/pocket cleanup: 1.0 mm flat end mill.

For Cherry MX resin socket:
- Best: 0.8 mm to 1.0 mm flat end mill.
- Socket slot nominal is about 1.32 mm wide, so a 1.0 mm tool leaves room for finishing.

## Conservative starting feeds for small 3020 router

These are starting points only; reduce them if the spindle, frame, or bit chatters.

Wood with 1-2 mm carbide end mill:
- Spindle: 12000-18000 RPM.
- Feed: 250-600 mm/min.
- Plunge: 80-150 mm/min.
- Stepdown: 0.3-0.8 mm.
- Stepover roughing: 35-45%.
- Stepover finishing: 8-12%.

Resin with 0.8-1.0 mm end mill:
- Spindle: 10000-16000 RPM.
- Feed: 150-400 mm/min.
- Plunge: 50-100 mm/min.
- Stepdown: 0.2-0.4 mm.

## CAM operation order

### Wood body

1. Face stock lightly if needed.
2. 3D rough the outside body from `keycap_1u_cherry_mx_wood_body.stl`.
3. 3D finish the top surface.
4. Machine the underside cavity and resin pocket.
5. Machine the square resin pour pocket to about 7.4 x 7.4 x 5.0 mm.
6. Leave 0.15-0.30 mm clearance for the resin insert/pour because wood and resin dimensions move.
7. Cut the outer profile last, with tabs if not using strong double-sided tape.

### Resin stem/insert

Two practical options:

Option A - cast resin into the wood pocket:
- Seal the wood first.
- Cast resin into the 7.4 x 7.4 x 5.0 mm square pocket.
- After curing, re-zero on the underside center and machine the Cherry MX female socket.

Option B - machine/print separate insert:
- CAM from `keycap_1u_cherry_mx_resin_insert.stl`.
- Test fit in the wood pocket.
- Bond with epoxy or thin CA after checking switch fit.

## Cherry MX fit check

Before making a full set, cut only the resin socket test:
- Slot pair: about 4.2 x 1.32 mm, centered.
- Available resin depth: about 5.0 mm.
- If switch is too tight, increase slot width by 0.05 mm.
- If switch is loose, reduce slot width or use a tougher resin/epoxy mix.

## Postprocessor

Choose the postprocessor that matches your controller:
- GRBL/Candle: use a GRBL post and output `.nc`.
- Mach3: use a Mach3 mill post and output `.tap` or `.nc`.
- Offline 3020 controller: check whether it expects `.nc`, `.tap`, or `.txt`.

Minimum G-code features to confirm:
- Uses millimeters: `G21`.
- Absolute coordinates: `G90`.
- Safe retracts clear your clamps.
- Spindle command matches your controller: commonly `M3 S...`.
- Program end is accepted: commonly `M5` then `M30`.

## Safety checklist

- Simulate in CAM.
- Run an air-cut 5-10 mm above stock.
- Keep one hand near emergency stop.
- Confirm tool diameter in CAM matches the real bit.
- Confirm Z zero before every operation.
- Confirm the tool does not collide with clamps.
- Make one sacrificial test in cheap wood before using final wood/resin.
