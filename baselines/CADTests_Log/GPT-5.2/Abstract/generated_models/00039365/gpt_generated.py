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
        height = 20.0
    
        # Parallelogram definition (2D points in XY)
        # A simple slanted rectangle: width W, height H, with x-shear S
        W = 80.0
        H = 50.0
        S = 20.0  # shear in +X for the top edge
    
        # Square hole size (must fit within the parallelogram)
        square_side = 25.0
    
        # --- Build parallelogram profile and extrude ---
        pts = [(0, 0), (W, 0), (W + S, H), (S, H)]
        base = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(height)
        )
    
        # --- Cut square hole through the solid ---
        result = (
            base
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .rect(square_side, square_side)
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00039365/gpt_generated.stl')
