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
        # Parameters (units as given; CadQuery uses mm by default but units are arbitrary here)
        length = 1.5
        width = 0.73113
        depth = 0.00472
    
        # Construct a scalene, obtuse triangle:
        # Base endpoints set to achieve overall X span = length.
        # Top vertex set to achieve overall Y span = width and to make the top angle obtuse.
        #
        # Points (before centering):
        # A = (-L/2, 0)
        # B = ( L/2, 0)
        # C = (cx, W) with cx chosen so angle at C is obtuse.
        A = (-length / 2.0, 0.0)
        B = ( length / 2.0, 0.0)
        C = (-0.55, width)  # off-center to be scalene; chosen to make angle at C obtuse
    
        # Center the triangle about the origin (centroid at (0,0))
        cx = (A[0] + B[0] + C[0]) / 3.0
        cy = (A[1] + B[1] + C[1]) / 3.0
        A = (A[0] - cx, A[1] - cy)
        B = (B[0] - cx, B[1] - cy)
        C = (C[0] - cx, C[1] - cy)
    
        tri = (
            cq.Workplane("XY")
            .moveTo(*A)
            .lineTo(*B)
            .lineTo(*C)
            .close()
            .extrude(depth)
        )
    
        return tri
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00005721/gpt_generated.stl')
