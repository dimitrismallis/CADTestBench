import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    from cadquery import selectors
    
    def create_cad() -> cq.Workplane:
        # Parameters (mm)
        length = 120.0   # long dimension (X)
        width  = 30.0    # short dimension (Y)
        thick  = 12.0    # extrusion (Z)
        fillet_r = 8.0   # radius for the two rounded corners
    
        # Two corners on one long edge: choose the +Y edge corners
        v1 = ( length / 2.0,  width / 2.0, 0)
        v2 = (-length / 2.0,  width / 2.0, 0)
    
        sk = (
            cq.Sketch()
            .rect(length, width)
            .vertices(selectors.NearestToPointSelector(v1)).fillet(fillet_r)
            .reset()
            .vertices(selectors.NearestToPointSelector(v2)).fillet(fillet_r)
        )
    
        result = cq.Workplane("XY").placeSketch(sk).extrude(thick)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997681/gpt_generated.stl')
