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
        length = 1.0
        width = 0.75
        height = 0.75
    
        cyl_od = 0.5
        wall = 0.05  # chosen wall thickness for "hollow" cylinder
        cyl_id = max(cyl_od - 2 * wall, 0.01)
    
        # Base rectangular prism (extruded rectangle)
        base = cq.Workplane("XY").rect(length, width).extrude(height)
    
        # Hollow cylinder (tube) centered on the rectangle, height equal to base height
        tube = (
            cq.Workplane("XY")
            .circle(cyl_od / 2)
            .circle(cyl_id / 2)
            .extrude(height)
        )
    
        # Combine
        result = base.union(tube)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00521895/gpt_generated.stl')
