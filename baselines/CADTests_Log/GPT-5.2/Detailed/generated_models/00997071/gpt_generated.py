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
        main_len = 0.636792   # X direction
        main_wid = 0.56638    # Y direction
    
        tab_len = 0.636792 + 0.113207 * 2  # X direction
        tab_wid = 0.141509                 # Y direction
    
        height = 0.099057
    
        hole_d = 0.318396
    
        # Tab centers are on the midpoints of the main rectangle's longer edges (±Y)
        tab_offset_y = main_wid / 2 + tab_wid / 2
    
        # Build 2D profile by union of rectangles, then extrude
        body = (
            cq.Workplane("XY")
            .rect(main_len, main_wid)
            .rect(tab_len, tab_wid, centered=True).center(0, tab_offset_y).rect(tab_len, tab_wid)
            .center(0, -2 * tab_offset_y).rect(tab_len, tab_wid)  # move from +tab_offset_y to -tab_offset_y
            .center(0, tab_offset_y)  # return to origin in Y
            .extrude(height)
        )
    
        # Cut center through-hole
        result = (
            body
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .hole(hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997071/gpt_generated.stl')
