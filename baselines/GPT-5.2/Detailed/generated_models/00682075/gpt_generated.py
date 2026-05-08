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
        # Units as given in prompt
        L0 = 0.75
        step_reduction = 0.25
        H_step = 0.25
        extrude_depth = 0.25
    
        L1 = L0 - step_reduction
        L2 = L0 - 2 * step_reduction
    
        # Build a closed "stair-step" profile in the XY plane:
        # X = length direction, Y = vertical (stacked steps)
        # Profile points (counter-clockwise), starting at bottom-left
        pts = [
            (0.0, 0.0),
            (L0, 0.0),
            (L0, H_step),
            (L1, H_step),
            (L1, 2 * H_step),
            (L2, 2 * H_step),
            (L2, 3 * H_step),
            (0.0, 3 * H_step),
        ]
    
        pedestal = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(extrude_depth)
            .translate((0.375, -0.25, -0.020659))
        )
    
        return pedestal
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00682075/gpt_generated.stl')
