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
        base_xy = 0.830095
        base_h = 0.1703531
    
        pocket_xy = 0.676879
        pocket_depth = 0.105467
    
        bottom_boss_d = 0.327945
        bottom_boss_h = 0.105467
    
        corner_boss_d = 0.25606
        corner_boss_h = 0.094448
    
        # Corner boss placement: "near a corner" -> use a rectangle inset from edges
        # Choose inset so bosses are clearly near corners but remain on the top face.
        inset = 0.12
        corner_rect = base_xy - 2 * inset  # spacing between opposite bosses in X and Y
    
        # Base solid
        result = (
            cq.Workplane("XY")
            .box(base_xy, base_xy, base_h, centered=(True, True, False))  # bottom at Z=0
        )
    
        # Pocket cut from the top face downward (does not remove the top face)
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(pocket_xy, pocket_xy)
            .cutBlind(-pocket_depth)
        )
    
        # Bottom centered cylinder (boss) extruded upward from the bottom face
        result = (
            result
            .faces("<Z").workplane(centerOption="CenterOfMass")
            .circle(bottom_boss_d / 2.0)
            .extrude(bottom_boss_h)
        )
    
        # Four top corner cylinders
        result = (
            result
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(corner_rect, corner_rect, forConstruction=True)
            .vertices()
            .circle(corner_boss_d / 2.0)
            .extrude(corner_boss_h)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00852000/gpt_generated.stl')
