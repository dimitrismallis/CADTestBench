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
        # --- Parameters (mm) ---
        length = 80.0   # longer side (X)
        width  = 40.0   # shorter side (Y)
        height = 20.0
    
        semi_r = 15.0
        cut_depth = 12.0
    
        # --- Base: rectangle sketch then extrude ---
        base = cq.Workplane("XY").rect(length, width).extrude(height)
    
        # --- Semicircle cutout on top face ---
        # Diameter lies on the +Y edge (a long side), running along X.
        y_edge = width / 2.0
        y_diam = y_edge                 # diameter line at the edge
        y_bulge = y_edge - semi_r       # bulge inward toward -Y
    
        cut = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            # Build a closed semicircle profile: arc + diameter line
            .moveTo(-semi_r, y_diam)
            .threePointArc((0.0, y_bulge), (semi_r, y_diam))  # arc bulging inward
            .lineTo(-semi_r, y_diam)                          # close along diameter (flat edge)
            .close()
            .cutBlind(-cut_depth)
        )
    
        return cut
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00995759/gpt_generated.stl')
