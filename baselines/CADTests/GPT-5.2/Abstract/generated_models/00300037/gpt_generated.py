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
        # U-shape overall size
        outer_w = 80.0
        outer_h = 60.0
    
        # Wall thickness and bottom bar thickness
        wall = 10.0
        bottom_bar = 12.0
    
        # Extrusion height
        height = 25.0
    
        # Corner squares (placed at bottom-left and bottom-right corners)
        sq = 18.0
        overlap = 3.0  # how much the squares overlap into the U's bottom corners
    
        # --- Derived dimensions for the inner cutout (to form the U) ---
        inner_w = outer_w - 2 * wall
        inner_h = outer_h - bottom_bar  # open at the top, leaving bottom bar thickness
    
        # --- Base U-shape: outer rectangle minus inner rectangle shifted upward ---
        u2d = (
            cq.Workplane("XY")
            .rect(outer_w, outer_h)
            .rect(inner_w, inner_h)
            .extrude(height)
        )
    
        # --- Add two squares on the top face, overlapping bottom corners slightly ---
        # Bottom-left corner of outer rectangle is (-outer_w/2, -outer_h/2)
        # Bottom-right corner is ( outer_w/2, -outer_h/2)
        left_center = (
            -outer_w / 2 + sq / 2 - overlap,
            -outer_h / 2 + sq / 2 - overlap
        )
        right_center = (
            outer_w / 2 - sq / 2 + overlap,
            -outer_h / 2 + sq / 2 - overlap
        )
    
        result = (
            u2d
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([left_center, right_center])
            .rect(sq, sq)
            .extrude(height, combine=True)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00300037/gpt_generated.stl')
