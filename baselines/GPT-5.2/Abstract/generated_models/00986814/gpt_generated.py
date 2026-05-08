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
        base_len = 80.0
        base_wid = 25.0
        base_thk = 4.0
    
        cyl_d = 10.0
        cyl_h = base_thk  # "same amount" as the base extrusion
        cyl_spacing = 14.0  # center-to-center spacing between the two cylinders
    
        end_margin_x = 12.0  # distance from rectangle end to cylinder centers
        y_offset = 0.0       # centered in Y on the rectangle
    
        # --- Base plate ---
        result = (
            cq.Workplane("XY")
            .rect(base_len, base_wid)
            .extrude(base_thk)
        )
    
        # --- Two cylinders on one end (on top face) ---
        x_center = (base_len / 2.0) - end_margin_x
        pts = [
            (x_center - cyl_spacing / 2.0, y_offset),
            (x_center + cyl_spacing / 2.0, y_offset),
        ]
    
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints(pts)
            .circle(cyl_d / 2.0)
            .extrude(cyl_h, combine=True)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00986814/gpt_generated.stl')
