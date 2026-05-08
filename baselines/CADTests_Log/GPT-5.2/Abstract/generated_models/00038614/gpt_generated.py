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
        outer_size = 80.0     # overall outside width/height
        frame_width = 10.0    # wall thickness of the frame
        thickness = 8.0       # Z thickness
    
        inner_size = outer_size - 2 * frame_width
        if inner_size <= 0:
            raise ValueError("frame_width too large for given outer_size")
    
        # --- Model ---
        frame = (
            cq.Workplane("XY")
            .rect(outer_size, outer_size)
            .extrude(thickness)
            .faces(">Z").workplane()
            .rect(inner_size, inner_size)
            .cutThruAll()
        )
    
        return frame
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00038614/gpt_generated.stl')
