import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters (units as given) ---
        cyl_d = 0.02262
        cyl_r = cyl_d / 2.0
        cyl_h = 0.75
    
        hole_d = 0.015476
        hole_r = hole_d / 2.0
    
        # Offsets "from the respective edges of the cylinder"
        # Interpreted as distance from the OUTER cylindrical surface toward the center (radial inset).
        # So radial distance from center = cyl_r - inset.
        inset_top = 0.004167
        inset_bot_1 = 0.123228
        inset_bot_2 = 0.06399
    
        # Convert to radial positions from center (clamped to be non-negative)
        r_top = max(0.0, cyl_r - inset_top)
        r_bot_1 = max(0.0, cyl_r - inset_bot_1)
        r_bot_2 = max(0.0, cyl_r - inset_bot_2)
    
        # --- Base solid ---
        part = cq.Workplane("XY").cylinder(cyl_h, cyl_r)
    
        # --- Holes ---
        # Place one hole "near the top" and two "near the bottom".
        # Since these are circular holes "within the cylinder", model them as through-holes
        # drilled from the top face (cutThruAll), with XY positions encoding the requested insets.
        #
        # Use different angular positions to avoid overlap and to make the "slightly closer to center"
        # bottom hole visually distinct.
        hole_pts = [
            ( r_top,   0.0),  # near top
            (-r_bot_1, 0.0),  # near bottom (further inset -> closer to center)
            ( 0.0,     r_bot_2),  # near bottom
        ]
    
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints(hole_pts)
            .hole(hole_d)  # through-hole by default when depth=None
        )
    
        # --- Rotate and translate for "proper orientation" ---
        # Rotate so cylinder axis aligns with +X, then translate to lift off origin slightly.
        part = (
            part
            .rotate((0, 0, 0), (0, 1, 0), 90)   # Z-axis -> X-axis
            .translate((0.1, 0.0, 0.05))
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00521230/gpt_generated.stl')
