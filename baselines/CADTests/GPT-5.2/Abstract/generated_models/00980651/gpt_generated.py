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
        hex_flat_to_flat = 40.0   # across flats (mm)
        hex_height = 20.0         # prism height (mm)
    
        # For a regular hexagon: across_flats = sqrt(3) * R (circumradius)
        R = hex_flat_to_flat / math.sqrt(3.0)
        cyl_radius = R * 0.92     # slightly smaller than hexagon
        cyl_height = hex_height / 2.0
    
        # --- Model ---
        hex_prism = (
            cq.Workplane("XY")
            .polygon(6, 2 * R)          # polygon() uses circumscribed circle diameter
            .extrude(hex_height)
        )
    
        result = (
            hex_prism
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(cyl_radius)
            .extrude(cyl_height)        # adds cylinder on top, half the hex height
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00980651/gpt_generated.stl')
