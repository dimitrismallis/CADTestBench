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
        # --- Parameters ---
        base_w = 80.0   # X direction
        base_h = 40.0   # Y direction
        thickness = 3.0
    
        # Hole is 1/8th the size of the original rectangle (both dimensions)
        hole_w = base_w / 8.0
        hole_h = base_h / 8.0
    
        # Position hole close to the bottom edge (negative Y), centered in X
        bottom_margin = 4.0
        hole_center_y = -base_h / 2.0 + bottom_margin + hole_h / 2.0
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            .rect(base_w, base_h)
            .extrude(thickness)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(0, hole_center_y)
            .rect(hole_w, hole_h)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00521025/gpt_generated.stl')
