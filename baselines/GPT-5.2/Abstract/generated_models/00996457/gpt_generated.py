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
        R_outer = 20.0          # radius of the two outer circles
        R_inner = 10.0          # radius of the two inner circles (hole)
        center_offset = 18.0    # distance between the two circle centers (overlap if < 2*R_outer)
        thickness = 8.0         # extrusion height
    
        # Centers for the two overlapping circles (symmetric about origin)
        c1 = (-center_offset / 2.0, 0.0)
        c2 = ( center_offset / 2.0, 0.0)
    
        # Build outer union profile (two overlapping circles)
        wp = cq.Workplane("XY")
        outer = (
            wp
            .pushPoints([c1, c2])
            .circle(R_outer)
        )
    
        # Cut inner union profile (two smaller overlapping circles, same centers)
        result = (
            outer
            .pushPoints([c1, c2])
            .circle(R_inner)
            .extrude(thickness)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00996457/gpt_generated.stl')
