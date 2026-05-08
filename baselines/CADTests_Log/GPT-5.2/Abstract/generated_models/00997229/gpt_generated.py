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
        handle_len = 140.0          # distance between end centers
        handle_w   = 22.0           # rectangle width
        thick      = 8.0            # extrusion thickness
    
        end1_od = 34.0              # left end outer diameter (smaller)
        end2_od = 40.0              # right end outer diameter (larger)
    
        end1_hole_d = 18.0          # left end hole diameter
        end2_hole_d = 22.0          # right end hole diameter
    
        # Derived end centers
        x1 = -handle_len / 2.0
        x2 =  handle_len / 2.0
    
        # --- 2D profile: rectangle + two circles as one combined face ---
        # Build as multiple pending wires, then make a face from them.
        blank = (
            cq.Workplane("XY")
            .rect(handle_len, handle_w)
            .moveTo(x1, 0).circle(end1_od / 2.0)
            .moveTo(x2, 0).circle(end2_od / 2.0)
            .combine()               # combine wires into a single face where possible
            .extrude(thick)
        )
    
        # --- Cut holes through the two ends ---
        blank = (
            blank.faces(">Z").workplane(centerOption="CenterOfMass")
            .center(x1, 0).hole(end1_hole_d)
            .center(x2 - x1, 0).hole(end2_hole_d)  # move from x1 to x2 in the same workplane
        )
    
        return blank
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997229/gpt_generated.stl')
