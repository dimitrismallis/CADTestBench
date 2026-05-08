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
        # Parameters (units as given)
        r_big = 0.489821
        r_small = 0.319623
        x_offset = 0.260308
        height = 0.006808
    
        # Circle centers (symmetric about origin)
        c1 = (-x_offset / 2.0, 0.0)
        c2 = ( x_offset / 2.0, 0.0)
    
        # Use Sketch API for 2D boolean operations, then extrude
        sk = (
            cq.Sketch()
            .push([c1, c2]).circle(r_big, mode="a")     # add two big circles
            .push([c1, c2]).circle(r_small, mode="s")   # subtract two small circles (holes)
        )
    
        result = cq.Workplane("XY").placeSketch(sk).extrude(height)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00996457/gpt_generated.stl')
