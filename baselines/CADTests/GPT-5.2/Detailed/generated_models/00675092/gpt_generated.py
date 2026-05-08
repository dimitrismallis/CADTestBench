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
        # Dimensions (units as given in prompt)
        base = 0.75      # along Z in the ZX plane
        height = 0.75    # along X in the ZX plane
        thickness = 0.03 # extrusion along Y
    
        # Build a right triangle in the ZX plane with right angle at the origin:
        # Points are (X, Z) in that plane's 2D coordinates.
        tri = (
            cq.Workplane("ZX")
            .moveTo(0, 0)
            .lineTo(height, 0)   # +X
            .lineTo(0, base)     # +Z
            .close()
            .extrude(thickness)  # extrudes normal to ZX plane => along +Y
        )
    
        # Center along Y: shift by -thickness/2 so Y spans [-t/2, +t/2]
        tri_centered = tri.translate((0, -thickness / 2.0, 0))
    
        return tri_centered
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00675092/gpt_generated.stl')
