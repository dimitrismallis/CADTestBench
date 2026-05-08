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
        L = 80.0          # overall length (X)
        W = 30.0          # overall width  (Y)  -> long edges are along X
        T = 8.0           # thickness (Z)
    
        corner_r = 6.0    # radius for the two rounded corners on the same long edge
        hole_d = 4.0      # hole diameter
        hole_edge_offset = 8.0  # how far in from the outer edges (approx) for hole centers
    
        # Choose the "top" long edge in the sketch: y = +W/2
        # Rounded corners will be at (±L/2, +W/2)
    
        # --- Base sketch with two rounded corners on the same long edge ---
        sk = (
            cq.Sketch()
            .rect(L, W)
            # Select the two vertices on the +Y long edge and fillet them
            .vertices(">Y").fillet(corner_r)
        )
    
        plate = cq.Workplane("XY").placeSketch(sk).extrude(T)
    
        # --- Holes on the top face, near the two rounded corners (same side as rounded edge) ---
        # Place hole centers near the rounded corners, slightly inset from the outer boundary.
        x_pos = (L / 2) - hole_edge_offset
        y_pos = (W / 2) - hole_edge_offset
    
        result = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints([(-x_pos, y_pos), (x_pos, y_pos)])
            .hole(hole_d)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00986712/gpt_generated.stl')
