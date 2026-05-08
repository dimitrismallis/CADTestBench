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
        L = 0.75     # length (X)
        W = 0.5      # width  (Y)
        H = 0.375    # height (Z)
    
        semi_d = 0.5357
        semi_r = semi_d / 2.0
    
        # Base block: sketch rectangle then extrude
        base = cq.Workplane("XY").rect(L, W).extrude(H)
    
        # Semi-circular cutout on one of the longer sides (use +Y side face).
        # Create a workplane on the +Y face; in that plane, X is along length and Y is along Z.
        # Place the semicircle so its flat edge (diameter) lies on the face (workplane Y=0),
        # and the arc extends into the solid (negative local Y direction).
        cut_profile = (
            base
            .faces(">Y").workplane(centerOption="CenterOfMass")
            .moveTo(0, 0)                 # diameter line will lie on the face
            .radiusArc((semi_r, 0), -semi_r)  # arc from (-r,0) to (r,0) via negative sag
        )
    
        # The above arc starts at current point; ensure we start at (-r,0)
        cut_profile = (
            base
            .faces(">Y").workplane(centerOption="CenterOfMass")
            .moveTo(-semi_r, 0)
            .radiusArc((semi_r, 0), -semi_r)  # semicircle bulging into the block
            .close()
            .cutBlind(-W)  # cut into the block across full width
        )
    
        return cut_profile
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00995759/gpt_generated.stl')
