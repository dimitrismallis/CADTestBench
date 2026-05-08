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
        # Parameters (mm)
        base_w = 60.0
        base_h = 40.0
        cut_w = 10.0
        cut_h = 8.0
        extrude_h = 4.0
    
        # Centers of the corner cutouts (bottom-left and bottom-right)
        bl_center = (-base_w / 2 + cut_w / 2, -base_h / 2 + cut_h / 2)
        br_center = ( base_w / 2 - cut_w / 2, -base_h / 2 + cut_h / 2)
    
        sk = (
            cq.Sketch()
            .rect(base_w, base_h)  # base
            .push([bl_center, br_center])
            .rect(cut_w, cut_h, mode="s")  # subtract the two corner rectangles
        )
    
        result = cq.Workplane("XY").placeSketch(sk).extrude(extrude_h)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00984234/gpt_generated.stl')
