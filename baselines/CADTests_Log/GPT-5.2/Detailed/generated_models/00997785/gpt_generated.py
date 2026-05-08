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
        hex_side = 1.50001
        hex_h = 0.409382
    
        sq_side = 0.867904
        sq_h = 0.272921
        sq_rot_deg = 45.0
    
        # For a regular n-gon in CadQuery: polygon(nSides, diameter)
        # diameter here is the circumscribed circle diameter (2*R).
        # For a regular hexagon, side length s = R, so diameter = 2*s.
        hex_diameter = 2.0 * hex_side
    
        base = cq.Workplane("XY").polygon(6, hex_diameter).extrude(hex_h)
    
        top = (
            base
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(sq_side, sq_side)
            .rotate((0, 0, 0), (0, 0, 1), sq_rot_deg)
            .extrude(sq_h)
        )
    
        return top
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997785/gpt_generated.stl')
