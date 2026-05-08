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
        # Parameters (units as provided by the prompt)
        length = 0.375     # tip-to-tip along X
        width = 0.11438    # tip-to-tip along Y
        height = 0.75      # extrusion height along +Z
    
        # Rhombus (diamond) vertices centered at origin
        pts = [
            ( length / 2.0, 0.0),
            ( 0.0,  width / 2.0),
            (-length / 2.0, 0.0),
            ( 0.0, -width / 2.0),
        ]
    
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00038438/gpt_generated.stl')
