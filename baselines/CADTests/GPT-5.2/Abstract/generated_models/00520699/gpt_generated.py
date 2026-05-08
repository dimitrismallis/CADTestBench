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
        bulb_r = 6.0            # small circle radius
        bulb_h = 4.0            # bulb extrusion height
    
        stem_w = 4.0            # narrow rectangle width
        stem_l = 80.0           # very long rectangle length (along +Y)
        stem_h = 3.0            # slightly less than bulb_h
    
        # --- Model ---
        bulb = cq.Workplane("XY").circle(bulb_r).extrude(bulb_h)
    
        # Add stem on top of bulb, attached at the top edge of the circle.
        # Place rectangle so its bottom edge touches y=0 (top edge of bulb in +Y direction),
        # and center it in X.
        stem = (
            bulb.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(0, stem_l / 2.0)     # shift so rectangle's bottom edge is at y=0
            .rect(stem_w, stem_l)
            .extrude(stem_h, combine=True)
        )
    
        return stem
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520699/gpt_generated.stl')
