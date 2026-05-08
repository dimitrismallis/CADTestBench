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
        # Parameters
        sides = 8
        across_corners_diameter = 40.0  # diameter of circumscribed circle (across corners)
        height = 10.0                   # extrusion height
    
        result = (
            cq.Workplane("XY")
            .polygon(sides, across_corners_diameter)
            .extrude(height)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00670441/gpt_generated.stl')
