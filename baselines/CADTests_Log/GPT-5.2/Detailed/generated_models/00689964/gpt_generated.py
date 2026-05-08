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
        side_len = 0.61859
        head_h = 0.214286
    
        shank_d = 0.321427
        shank_h = 0.75025
    
        # For a regular hexagon:
        # side length s equals circumradius R, and across-flats = 2 * apothem = sqrt(3) * s
        across_flats = math.sqrt(3.0) * side_len
    
        # --- Model ---
        head = (
            cq.Workplane("XY")
            .polygon(6, across_flats)   # polygon(diameter) uses across-flats for even-sided polygons
            .extrude(head_h)
        )
    
        screw = (
            head
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(shank_d / 2.0)
            .extrude(shank_h)
        )
    
        return screw
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00689964/gpt_generated.stl')
