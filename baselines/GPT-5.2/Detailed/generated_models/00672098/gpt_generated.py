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
        L = 0.337772   # length in X
        W = 0.75       # width in Y
        H = 0.021792   # base height in Z
    
        margin = 0.01816  # margin on left/right and top
    
        # Small extra extrusion to thicken the U shape upward
        extra_extrude = 0.01
    
        # Inner cutout dimensions:
        # - leave margin on both X sides => subtract 2*margin from length
        inner_L = L - 2 * margin
        # - leave margin on the "top" (+Y) only, and open on bottom (-Y)
        inner_W = W - margin
    
        # Center of the cutout in Y so that its top edge is at +W/2 - margin
        # and its bottom edge is at -W/2 (flush/open).
        cutout_center_y = -margin / 2.0
    
        # Base solid
        base = cq.Workplane("XY").box(L, W, H, centered=True)
    
        # Cut the U opening from the top face down through the base
        u_base = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .center(0, cutout_center_y)
            .rect(inner_L, inner_W)
            .cutThruAll()
        )
    
        # Extrude the remaining U-shaped top profile upward a small amount
        result = (
            u_base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .add(u_base.faces(">Z").wires().toPending())
            .extrude(extra_extrude)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00672098/gpt_generated.stl')
