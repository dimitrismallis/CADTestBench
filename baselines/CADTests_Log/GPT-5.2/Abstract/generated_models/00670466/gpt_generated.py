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
        base = 80.0      # long base
        height = 8.0     # small height -> base angles close to 90 degrees
        thickness = 20.0 # extrusion height
    
        # Isosceles triangle vertices (centered about X=0)
        p1 = (-base / 2.0, 0.0)
        p2 = ( base / 2.0, 0.0)
        p3 = (0.0, height)
    
        tri = (
            cq.Workplane("XY")
            .moveTo(*p1)
            .lineTo(*p2)
            .lineTo(*p3)
            .close()
            .extrude(thickness)
        )
    
        return tri
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670466/gpt_generated.stl')
