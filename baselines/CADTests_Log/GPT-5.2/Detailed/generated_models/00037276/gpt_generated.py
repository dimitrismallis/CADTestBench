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
        # --- Given dimensions (units as provided) ---
        d_big = 0.485133
        d_small = 0.157385
        total_len = 0.993343
        width = 0.243343
    
        r_big = d_big / 2.0
        r_small = d_small / 2.0
    
        # As described: separation approximately equals:
        # total length - (sum of radii)
        center_sep = total_len - (r_big + r_small)
    
        # Place circle centers along X axis, symmetric about origin
        x_big = -center_sep / 2.0
        x_small = center_sep / 2.0
    
        # Build a "taut chain/belt" outline using convex hull of the two circles.
        # The hull produces the two external tangents and the appropriate arcs.
        sketch = (
            cq.Sketch()
            .circle(r_big).moved(x_big, 0)
            .circle(r_small).moved(x_small, 0)
            .hull()
        )
    
        result = cq.Workplane("XY").placeSketch(sketch).extrude(width)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00037276/gpt_generated.stl')
