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
        # Parameters (units as given)
        diameter = 0.955953
        radius = diameter / 2.0
        width = 0.295686
    
        trap_base = 0.163062
        trap_top = trap_base  # equal per prompt
        offset = 0.698688
        trap_h = diameter - offset  # requested height
    
        # 1) Base cylinder (disk extruded)
        part = cq.Workplane("XY").circle(radius).extrude(width)
    
        # 2) Cut out the small trapezium (here: rectangle since top==base) from the top
        # Place the cut so its top edge is at y = +radius (top of circle), centered in X.
        y_center = radius - trap_h / 2.0
    
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(0, y_center)
            .rect(trap_base, trap_h, centered=True)
            .cutThruAll()
        )
    
        # 3) Translate as specified
        part = part.translate((0, width / 2.0, -0.272116))
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00681831/gpt_generated.stl')
