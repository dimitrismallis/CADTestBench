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
        top_base = 30.0      # shorter base (centered over bottom base)
        height = 25.0        # trapezium height in Y
        prism_length = 40.0  # extrusion distance in Z
    
        # Half-widths for symmetric (regular/isosceles) trapezium
        b = bottom_base / 2.0
        t = top_base / 2.0
        h = height
    
        # Trapezium vertices (counter-clockwise), centered about X=0
        pts = [(-b, 0), (b, 0), (t, h), (-t, h)]
    
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(prism_length)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00985494/gpt_generated.stl')
