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
        cube_L = 0.747683
    
        tri_leg = 0.498375          # base length and height (right triangle legs)
        prism_extrude = cube_L      # extrusion length equal to cube length
    
        # --- Cube (centered at origin) ---
        cube = cq.Workplane("XY").box(cube_L, cube_L, cube_L, centered=True)
    
        # --- Right triangular prism ---
        # Right triangle in XY with right angle at (0,0), legs along +X and +Y
        prism = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(tri_leg, 0)
            .lineTo(0, tri_leg)
            .close()
            .extrude(prism_extrude)   # extrudes from z=0 to z=+prism_extrude
        )
    
        # Place prism so its right-angle corner is at cube's top-front-left corner:
        # cube corner = (-L/2, -L/2, +L/2)
        prism = prism.translate((-cube_L / 2, -cube_L / 2, cube_L / 2))
    
        # Combine into one model (they touch; union is fine even if only face/edge contact)
        result = cube.union(prism)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00017291/gpt_generated.stl')
