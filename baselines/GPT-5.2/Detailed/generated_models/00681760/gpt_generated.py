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
        # Parameters (units as given)
        L = 0.525    # rectangle length (X)
        W = 0.75     # rectangle width  (Y) and extrusion distance
        H = 0.1125   # rectangle height (Z) and trapezium height in sketch (X-direction)
        b_long = L   # trapezium longer base
        b_short = 0.3
        trap_h = H   # trapezium height (distance between bases in sketch)
    
        # Base block: length along X, width along Y, height along Z
        base = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # Build the attached trapezium on the top face.
        # We sketch in the XZ plane (on top face, workplane is XY; we want a profile in XZ
        # that will be extruded along Y). So we use a workplane on the top face and then
        # transform so sketch plane is XZ with Y as extrusion direction.
        #
        # Easiest: use "front" (XZ) plane for the profile, then extrude along Y, and union
        # with the base. Place the base so its top is at z=H/2, and align the trapezium so
        # its short base lies on the top edge of the rectangle at z=H/2.
        #
        # Profile coordinates in XZ:
        # - Rectangle occupies z in [-H/2, +H/2] and x in [-L/2, +L/2]
        # - Trapezium sits on top: its short base lies at z=+H/2, centered in X.
        #   Its long base lies at z=+H/2 + trap_h, with length b_long (=L).
        x0s, x1s = -b_short/2, b_short/2
        x0l, x1l = -b_long/2,  b_long/2
        z_short = H/2
        z_long  = H/2 + trap_h
    
        profile = (
            cq.Workplane("XZ")
            # rectangle profile (base block cross-section)
            .rect(L, H, centered=True)
            # add trapezium attached to the top edge (short base at z=H/2)
            .moveTo(x0s, z_short)
            .lineTo(x1s, z_short)
            .lineTo(x1l, z_long)
            .lineTo(x0l, z_long)
            .close()
        )
    
        # Extrude the combined profile along Y by the rectangle width
        tiered = profile.extrude(W, both=True)
    
        # The tiered solid already includes the base rectangle cross-section, so it is the final part.
        # Ensure centered: extrude both=True centers along Y; profile is centered in X and Z.
        return tiered
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00681760/gpt_generated.stl')
