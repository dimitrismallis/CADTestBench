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
        height = 0.010714
        od = 1.5
        id_subtract = 0.342858  # 0.171429*2
        id_ = od - id_subtract
    
        hole_d = 0.105429
    
        # Radii
        ro = od / 2.0
        ri = id_ / 2.0
    
        # Centers located at: (od/2 - (od - id)/4)
        hole_r = (od / 2.0) - ((od - id_) / 4.0)
    
        # --- Model ---
        ring = (
            cq.Workplane("XY")
            .circle(ro)
            .circle(ri)
            .extrude(height)
        )
    
        # 3 holes, equidistant (120° apart) on the computed radius
        ring = (
            ring.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .polarArray(hole_r, 0, 360, 3)
            .hole(hole_d)
        )
    
        # Rotate final object -90 degrees about Z axis
        ring = ring.rotate((0, 0, 0), (0, 0, 1), -90)
    
        return ring
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00521000/gpt_generated.stl')
