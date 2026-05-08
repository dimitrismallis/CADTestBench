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
        base_len = 0.75   # X
        base_wid = 0.5    # Y
        base_h   = 0.75   # Z
    
        cut_len  = 0.25   # X
        cut_wid  = 0.5    # Y (full width)
        cut_depth = 0.25  # Z (negative extrude depth)
    
        # Base solid
        result = (
            cq.Workplane("XY")
            .rect(base_len, base_wid)
            .extrude(base_h)
        )
    
        # Cutout: on top face, place rectangle centered in X, aligned to top edge in Y
        # Base top edge in Y is at +base_wid/2. For a cut rectangle of height cut_wid,
        # to align its top edge to +base_wid/2, its center must be at:
        # y_center = +base_wid/2 - cut_wid/2
        y_center = (base_wid / 2.0) - (cut_wid / 2.0)
    
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(0, y_center)
            .rect(cut_len, cut_wid)
            .cutBlind(cut_depth)  # cuts downward from the top face
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00682073/gpt_generated.stl')
