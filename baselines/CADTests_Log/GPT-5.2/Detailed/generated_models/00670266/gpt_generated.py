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
        L = 1.08869      # length (X)
        W = 0.870954     # width  (Y)
        fillet_r = 0.217746
        thickness = 0.108869
    
        hole_d = 0.195965
        hole_offset_from_left = 0.228625  # from left edge along X
    
        # Hole position
        hole_x = (-L / 2.0) + hole_offset_from_left
        hole_y = (W / 2.0) - fillet_r  # "just below" the top edge
    
        tag = (
            cq.Workplane("XY")
            .rect(L, W)
            .extrude(thickness)
            # Fillet the two top corners: pick top-face vertices at max Y,
            # then select their ancestor edges (vertical ones) and fillet.
            .faces(">Z")
            .vertices(">Y")
            .ancestors("Edge")
            .edges("|Z")
            .fillet(fillet_r)
        )
    
        tag = (
            tag.faces(">Z")
            .workplane(centerOption="CenterOfMass")
            .center(hole_x, hole_y)
            .hole(hole_d)
        )
    
        return tag
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00670266/gpt_generated.stl')
