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
        square_len = 1.1056     # X size of central rectangle
        square_wid = 1.22951    # Y size of central rectangle
    
        tab_len = 1.76342       # X size of each side rectangle
        tab_wid = 0.368852      # Y size of each side rectangle
        # "height of each rectangle is twice its width" refers to 3D height,
        # but the request later specifies a single extrude depth for the whole sketch.
        extrude_depth = 0.122951
    
        # Tabs centered on horizontal centerline (y=0) and attached to left/right edges
        x_offset = (square_len / 2.0) + (tab_len / 2.0)
    
        sk = (
            cq.Sketch()
            .rect(square_len, square_wid)                 # central profile
            .rect(tab_len, tab_wid, mode="a").moved(x=x_offset, y=0)   # right tab
            .rect(tab_len, tab_wid, mode="a").moved(x=-x_offset, y=0)  # left tab
        )
    
        result = cq.Workplane("XY").placeSketch(sk).extrude(extrude_depth)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997065/gpt_generated.stl')
