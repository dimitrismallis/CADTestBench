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
        top_width = 30.0      # shorter parallel side
        bottom_width = 60.0   # longer parallel side
        height = 20.0         # distance between parallel sides
        length = 200.0        # extrusion distance (long prism)
    
        # Half-widths for symmetric (isosceles) trapezium
        tw = top_width / 2.0
        bw = bottom_width / 2.0
        h = height
    
        # Trapezium vertices (counter-clockwise), centered about origin
        pts = [
            (-bw, -h/2),  # bottom-left
            ( bw, -h/2),  # bottom-right
            ( tw,  h/2),  # top-right
            (-tw,  h/2),  # top-left
        ]
    
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(length)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00998283/gpt_generated.stl')
