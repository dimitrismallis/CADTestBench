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
        bottom_base = 60.0   # longer base
        top_base = 30.0      # shorter base
        height = 25.0        # trapezoid height in Y direction
        thickness = 10.0     # extrusion in Z
    
        if top_base >= bottom_base:
            raise ValueError("For a trapezoid, top_base must be smaller than bottom_base.")
        if height <= 0 or thickness <= 0:
            raise ValueError("height and thickness must be positive.")
    
        # Define vertices (counter-clockwise), centered about X=0 for isosceles symmetry
        # Bottom base at y=0, top base at y=height
        pts = [
            (-bottom_base / 2.0, 0.0),
            ( bottom_base / 2.0, 0.0),
            ( top_base / 2.0,    height),
            (-top_base / 2.0,    height),
        ]
    
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(thickness)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520570/gpt_generated.stl')
