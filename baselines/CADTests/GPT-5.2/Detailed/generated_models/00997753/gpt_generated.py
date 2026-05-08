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
        outer_size = 1.5
        outer_fillet_r = 0.157235
        height = 0.655147
    
        inner_size = 1.44759
        inner_fillet_r = 0.13103
        cut_depth = 0.655147
    
        # --- Outer profile as a 2D sketch with filleted corners ---
        outer_sk = (
            cq.Sketch()
            .rect(outer_size, outer_size)
            .vertices()
            .fillet(outer_fillet_r)
        )
    
        outer = cq.Workplane("XY").placeSketch(outer_sk).extrude(height)
    
        # --- Inner cavity profile as a 2D sketch with filleted corners ---
        inner_sk = (
            cq.Sketch()
            .rect(inner_size, inner_size)
            .vertices()
            .fillet(inner_fillet_r)
        )
    
        mold = (
            outer
            .faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .placeSketch(inner_sk)
            .cutBlind(-cut_depth)  # cut downward from the top face
        )
    
        # Translate vertically by half the height (bottom at Z=0)
        mold = mold.translate((0, 0, height / 2.0))
    
        return mold
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997753/gpt_generated.stl')
