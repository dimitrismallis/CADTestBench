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
        # Parameters
        L = 40.0                 # cube side length
        s = L / 4.0              # "1/4th the size" linear scale
    
        # --- Shape 1: large cube (centered) ---
        cube = cq.Workplane("XY").box(L, L, L, centered=True)
    
        # --- Shape 2: right triangular prism ---
        # Right triangle in the YZ plane with legs s (along -Y and +Z), extruded along +X by s.
        # Triangle vertices (in YZ): (0,0), (-s,0), (0,s)
        prism = (
            cq.Workplane("YZ")
            .polyline([(0, 0), (-s, 0), (0, s)])
            .close()
            .extrude(s)  # extrude along +X (normal of YZ plane)
        )
    
        # Position prism so it touches cube at x = +L/2, and align two edges:
        # - Prism's vertical edge at y=0 aligns with cube's vertical edge at y=+L/2
        # - Prism's bottom edge at z=0 aligns with cube's bottom edge at z=-L/2
        # Also ensure contact at the cube's +X face.
        prism = prism.translate((L/2, L/2, -L/2))
    
        # Return both shapes as a single compound/workplane
        final_result = cube.union(prism)
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00017291/gpt_generated.stl')
