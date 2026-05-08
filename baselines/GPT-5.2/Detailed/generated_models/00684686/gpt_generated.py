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
        # Base dimensions
        base_len_x = 0.231564
        base_wid_y = 0.028954
        base_h_z   = 0.926255
    
        # Rectangular hole (cut) dimensions in X and Z (as described)
        hole_len_x = 0.12897
        hole_h_z   = 0.479215
        bottom_gap = 0.005463
    
        # Translation
        tx, ty, tz = (-0.050509, -0.014477, 0.286873)
    
        # Base solid: centered in X/Y, bottom at Z=0
        part = (
            cq.Workplane("XY")
            .rect(base_len_x, base_wid_y)
            .extrude(base_h_z)
        )
    
        # Cut a rectangle on the front face (Y=0 plane), extrude through full width in Y
        # Place the cut so its bottom is at Z=bottom_gap:
        # On the XZ workplane, rectangle is centered at z = bottom_gap + hole_h_z/2
        z_center = bottom_gap + hole_h_z / 2.0
    
        part = (
            part
            .faces(">Y").workplane(centerOption="CenterOfMass")
            .center(0, z_center - base_h_z / 2.0)  # workplane origin is at face COM (z=base_h/2)
            .rect(hole_len_x, hole_h_z)
            .cutBlind(-base_wid_y)  # cut through the full thickness (toward -Y)
        )
    
        # Final placement
        part = part.translate((tx, ty, tz))
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00684686/gpt_generated.stl')
