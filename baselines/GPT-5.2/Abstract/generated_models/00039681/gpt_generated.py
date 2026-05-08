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
        # --- Parameters ---
        outer_d = 30.0          # constant outer diameter for both halves
        total_len = 30.0
        half_len = total_len / 2.0
    
        # Inner diameters: small is ~2/3 of large
        inner_d_large = 18.0
        inner_d_small = (2.0 / 3.0) * inner_d_large  # = 12.0
    
        # Radii
        outer_r = outer_d / 2.0
        inner_r_small = inner_d_small / 2.0
        inner_r_large = inner_d_large / 2.0
    
        # --- First half: smaller hole ---
        part = (
            cq.Workplane("XY")
            .circle(outer_r)
            .circle(inner_r_small)
            .extrude(half_len)
        )
    
        # --- Second half: larger hole, extruded from the end of the first half ---
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(outer_r)
            .circle(inner_r_large)
            .extrude(half_len)
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00039681/gpt_generated.stl')
