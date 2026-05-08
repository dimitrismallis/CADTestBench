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
        # --- Parameters (units as given) ---
        length = 0.25
        width = 0.75
        base_h = 0.02
    
        cyl_d = 0.07
        cyl_r = cyl_d / 2.0
        cyl_h = 0.04
    
        # Placement parameters for the two cylinders
        end_margin = 0.03          # distance from the end of the rectangle
        center_spacing = 0.08      # spacing between cylinder centers (next to each other)
    
        # Base: rectangle sketch extruded
        base = cq.Workplane("XY").rect(length, width).extrude(base_h)
    
        # Two cylinders on one end of the rectangle (on the top face)
        # Put them near the +X end, side-by-side along Y.
        x_pos = (length / 2.0) - end_margin
        pts = [(x_pos, -center_spacing / 2.0), (x_pos, center_spacing / 2.0)]
    
        result = (
            base
            .faces(">Z").workplane()
            .pushPoints(pts)
            .circle(cyl_r)
            .extrude(cyl_h)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00986814/gpt_generated.stl')
