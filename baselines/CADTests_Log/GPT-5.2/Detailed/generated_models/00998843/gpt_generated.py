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
        base_len = 0.5
        base_wid = 0.75
        tier_len = 0.5
        tier_wid = 0.35
        h1 = 0.15
        h2 = 0.15
        hole_d = 0.2
    
        # Base block (centered on origin in XY by default)
        part = cq.Workplane("XY").rect(base_len, base_wid).extrude(h1)
    
        # Upper tier: same length, reduced width, positioned at one end (in +Y direction)
        # Shift in Y by (base_wid - tier_wid)/2 to align the tier to the +Y edge of the base.
        y_shift = (base_wid - tier_wid) / 2.0
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(0, y_shift)
            .rect(tier_len, tier_wid)
            .extrude(h2)
        )
    
        # Hole through center of upper block (and through entire part)
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .hole(hole_d)
        )
    
        # Center the whole model at the origin using bounding box center
        solid = part.findSolid()
        bb = solid.BoundingBox()
        cx = (bb.xmin + bb.xmax) / 2.0
        cy = (bb.ymin + bb.ymax) / 2.0
        cz = (bb.zmin + bb.zmax) / 2.0
    
        part = part.translate((-cx, -cy, -cz))
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00998843/gpt_generated.stl')
