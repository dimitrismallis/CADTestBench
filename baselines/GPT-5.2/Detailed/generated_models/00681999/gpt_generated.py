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
        # Parameters (units as given in prompt)
        rect_w = 0.75
        rect_h = 0.5
        cut_s = 0.25
        depth = 0.25
    
        # Rectangle centered at origin => top edge at +rect_h/2
        # Square top edge aligned to rectangle top edge => square center y:
        cut_center_y = rect_h / 2 - cut_s / 2
    
        # Base face
        base = cq.Workplane("XY").rect(rect_w, rect_h).extrude(depth)
    
        # Cutout solid (extruded through the full depth)
        cutter = (
            cq.Workplane("XY")
            .center(0, cut_center_y)
            .rect(cut_s, cut_s)
            .extrude(depth)
        )
    
        result = base.cut(cutter)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00681999/gpt_generated.stl')
