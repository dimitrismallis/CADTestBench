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
        base_len = 80.0
        base_ht  = 40.0
        base_thk = 4.0   # "slightly extrude"
    
        cut_len = 30.0
        cut_ht  = 12.0
        cut_depth = 3.0  # "slight" cut (not thru all)
    
        # Positioning:
        # midpoint of length => x = 0 (since base is centered)
        # slightly above midpoint of height => y = +offset
        y_offset = 6.0
    
        # --- Model ---
        base = cq.Workplane("XY").rect(base_len, base_ht).extrude(base_thk)
    
        result = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(0, y_offset)
            .rect(cut_len, cut_ht)
            .cutBlind(-cut_depth)  # cut downward from top face
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00002298/gpt_generated.stl')
