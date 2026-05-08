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
        base_L = 1.5
        base_W = 0.75
        base_T = 0.034954
    
        col_L = 0.35911
        col_W = 0.581568
        col_H = 0.699153
    
        margin = 0.055864  # margin from base edge to column edge (along length)
    
        # Column center offset from part center along X:
        # base half-length minus margin minus half column length
        x_off = (base_L / 2.0) - margin - (col_L / 2.0)
    
        # --- Model ---
        part = (
            cq.Workplane("XY")
            .rect(base_L, base_W)
            .extrude(base_T)  # base plate from z=0 to z=base_T
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([(-x_off, 0.0), (x_off, 0.0)])
            .rect(col_L, col_W)
            .extrude(col_H)   # columns from z=base_T to z=base_T+col_H
        )
    
        # Translate so that the base of the columns (z=base_T) aligns with the bottom of the base (z=0)
        part = part.translate((0, 0, -base_T))
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997677/gpt_generated.stl')
