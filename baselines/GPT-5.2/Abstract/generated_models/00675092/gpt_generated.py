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
        # Parameters (mm)
        base = 60.0      # triangle base length along X
        height = 40.0    # triangle height along Y
        thickness = 3.0  # marginal extrusion thickness along Z
    
        # Right triangle with vertices at (0,0), (base,0), (0,height)
        tri = (
            cq.Workplane("XY")
            .polyline([(0, 0), (base, 0), (0, height)])
            .close()
            .extrude(thickness)
        )
    
        return tri
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00675092/gpt_generated.stl')
