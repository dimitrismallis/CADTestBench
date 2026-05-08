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
        length = 0.333015
        width = 0.908225
        height = 0.006055
    
        cut_w = 0.090822
        cut_h = 0.090822
        cut_depth = height  # as deep as the rectangle height
    
        # Base block (centered on origin)
        base = cq.Workplane("XY").box(length, width, height, centered=True)
    
        # Corner cutout center positions (relative to block center)
        x_off = (length / 2) - (cut_w / 2)
        y_off = (width / 2) - (cut_h / 2)
        corner_pts = [
            ( x_off,  y_off),
            (-x_off,  y_off),
            (-x_off, -y_off),
            ( x_off, -y_off),
        ]
    
        # Cut squares from the top face down through the full thickness
        result = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints(corner_pts)
            .rect(cut_w, cut_h)
            .cutBlind(-cut_depth)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670274/gpt_generated.stl')
