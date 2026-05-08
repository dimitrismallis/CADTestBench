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
        # --- Parameters (mm) ---
        head_flat_to_flat = 12.0   # hex head size across flats
        head_height = 5.0          # hex head thickness
        shank_diameter = 6.0       # bolt/screw shank diameter
        shank_length = 25.0        # shank length above the head
    
        # Convert across-flats to circumscribed circle diameter for cq.polygon()
        # For a regular hexagon: across_flats = 2 * R * cos(pi/6) = R * sqrt(3)
        # where R is circumradius. So R = across_flats / sqrt(3)
        # cq.polygon(n, diameter) uses the diameter of the circumscribed circle = 2R
        hex_circ_diam = 2.0 * (head_flat_to_flat / math.sqrt(3.0))
    
        # --- Model ---
        head = (
            cq.Workplane("XY")
            .polygon(6, hex_circ_diam)
            .extrude(head_height)
        )
    
        screw = (
            head
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(shank_diameter / 2.0)
            .extrude(shank_length)
        )
    
        return screw
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00689964/gpt_generated.stl')
