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
        base_len = 0.03547
        base_wid = 1.27689
        base_h   = 0.14188
    
        hole_len = 0.03547
        hole_wid = 0.5677508
        hole_depth = 0.094585  # cut depth into the plate from the top
    
        padding = 0.047292     # gap between the two holes (along Y)
    
        y_offset_final = 0.111555
    
        # --- Derived placement ---
        # Two holes symmetric about Y=0, with a clear gap = padding between them.
        # Center-to-center spacing along Y:
        hole_center_spacing = hole_wid + padding
        y_centers = [-hole_center_spacing / 2.0, hole_center_spacing / 2.0]
    
        # --- Base plate ---
        part = cq.Workplane("XY").box(base_len, base_wid, base_h, centered=True)
    
        # --- Cut the two rectangular holes from the top face ---
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([(0.0, y) for y in y_centers])
            .rect(hole_len, hole_wid)
            .cutBlind(-hole_depth)  # negative: cut downward from the top face
        )
    
        # --- Final translation ---
        # X already centered; apply requested Y offset; Z already centered (box centered=True)
        part = part.translate((0.0, y_offset_final, 0.0))
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00521437/gpt_generated.stl')
