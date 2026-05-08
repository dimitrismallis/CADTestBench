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
        # Units are treated as mm by CadQuery; using the given values directly.
        L = 1.125
        W = 1.5
        H = 0.039474
    
        hole_d = 0.059211
        inset_L = 0.108553  # inset from left/right edges along length (X)
        inset_W = 0.098684  # inset from top/bottom edges along width (Y)
    
        # Base "page"
        page = cq.Workplane("XY").rect(L, W).extrude(H)
    
        # Hole locations: inset rectangle corners; take the two left-side corners (top/bottom)
        hole_rect_L = L - 2 * inset_L
        hole_rect_W = W - 2 * inset_W
    
        result = (
            page
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(hole_rect_L, hole_rect_W, forConstruction=True)
            .vertices("<X")  # left-side two vertices => top-left and bottom-left
            .hole(hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670454/gpt_generated.stl')
