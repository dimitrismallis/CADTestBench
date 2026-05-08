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
        hex_flat_to_flat = 60.0   # across flats
        hex_height = 12.0
    
        square_size = 28.0        # side length
        square_height = 18.0
        square_rotation_deg = 45.0  # ensures no square edge is parallel to hex edges
    
        # Convert hex across-flats to circumscribed diameter for cq.polygon()
        # For a regular hexagon: across_flats = sqrt(3) * R, where R is circumradius
        # polygon(n, diameter) expects circumscribed diameter = 2R
        hex_circ_diam = 2.0 * (hex_flat_to_flat / math.sqrt(3.0))
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            .polygon(6, hex_circ_diam)
            .extrude(hex_height)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .rect(square_size, square_size)
            .rotate((0, 0, 0), (0, 0, 1), square_rotation_deg)
            .extrude(square_height)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00997785/gpt_generated.stl')
