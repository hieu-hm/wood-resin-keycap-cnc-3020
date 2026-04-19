# Keycap 1u Cherry MX - wood body + resin stem insert

Units: millimeters.

Generated files:
- `keycap_1u_cherry_mx_wood_body.stl`: wooden outer keycap shell.
- `keycap_1u_cherry_mx_resin_insert.stl`: square resin insert/pour block with underside Cherry MX female socket.
- `keycap_1u_cherry_mx_wood_resin_assembly.stl`: combined preview assembly.
- `keycap_1u_cherry_mx_layout.svg`: 2D dimension reference for bottom/top/pocket/stem.

Nominal dimensions:
- 1u outside bottom: 18.2 x 18.2 mm.
- Top face: 12.8 x 12.8 mm.
- Height: 9.6 mm.
- Wall thickness: 1.25 mm.
- Top thickness: 1.65 mm.
- Resin pour pocket: 7.4 x 7.4 x 5.0 mm under the top.
- Cherry MX female socket: centered, about 4.2 x 1.32 mm each slot, depth about 5.0 mm available in resin.

Manufacturing notes:
- This is a practical starting model, not an official Cherry MX mechanical drawing.
- For CNC wood, leave 0.15-0.30 mm extra clearance around the resin insert depending on wood movement and resin shrinkage.
- Do a fit test before making a full set. Cherry-compatible switches and printers/CNC postprocessors vary.
- For resin casting, machine/print the wood body first, seal the wood, cast resin into the 7.4 x 7.4 x 5.0 mm square pocket, then finish-machine the Cherry MX socket in the resin if your casting process cannot hold that detail.
- For a production STEP file, remodel this parametric design in Fusion 360/SolidWorks/FreeCAD from the dimensions above and then toolpath from STEP.
