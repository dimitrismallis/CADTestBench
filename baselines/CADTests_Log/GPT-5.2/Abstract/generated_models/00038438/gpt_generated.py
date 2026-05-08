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
        diag_x = 60.0   # full diagonal length along X
        diag_y = 30.0   # full diagonal length along Y
        height = 12.0   # extrusion height
    
        # Rhombus vertices (diamond) centered at origin
        pts = [
            ( diag_x / 2.0, 0.0),
            ( 0.0,  diag_y / 2.0),
            (-diag_x / 2.0, 0.0),
            ( 0.0, -diag_y / 2.0),
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
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00038438/gpt_generated.stl')
