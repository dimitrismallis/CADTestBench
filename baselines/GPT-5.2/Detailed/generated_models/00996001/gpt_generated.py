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
        web_thk = 0.083333
        col_w = 0.416667
        height = 0.475
        hole_d = 0.1375
    
        # Choose a reasonable overall span for the "table" (not specified),
        # consistent with the given thicknesses.
        inner_gap = 1.0  # clear opening between the two columns
    
        outer_w = inner_gap + 2 * col_w
        outer_h = web_thk + 2 * col_w  # gives a U with two side columns and a top web
    
        inner_w = inner_gap
        inner_h = outer_h - web_thk  # leaves the top web thickness
    
        # --- Build U-shaped sketch (outer rectangle minus inner rectangle) ---
        u_profile = (
            cq.Workplane("XY")
            .rect(outer_w, outer_h)
            .rect(inner_w, inner_h)   # second wire becomes an inner cutout during extrude
            .extrude(height)
        )
    
        # --- Hole at center of the horizontal surface (top face) ---
        result = (
            u_profile
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .hole(hole_d)  # through-hole
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00996001/gpt_generated.stl')
