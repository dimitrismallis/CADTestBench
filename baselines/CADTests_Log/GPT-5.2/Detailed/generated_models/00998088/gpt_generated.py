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
        L = 1.5
        W = 0.413793
        H = 0.031034
    
        cut_L = (L - 1.28276) / 2.0
        cut_W = W - 0.31034
        fillet_r = 0.025
    
        # Symmetric placement near left/right ends, aligned with plate edges
        x_off = (L / 2.0) - (cut_L / 2.0)
        y_off = 0.0
    
        # --- Base plate ---
        plate = cq.Workplane("XY").rect(L, W).extrude(H)
    
        # --- Cutout sketches ---
        # Right cutout: fillet the two corners on the outer side (max X of the cutout)
        cut_sk_right = (
            cq.Sketch()
            .rect(cut_L, cut_W)
            .vertices(">X")
            .fillet(fillet_r)
        )
    
        # Left cutout: fillet the two corners on the outer side (min X of the cutout)
        cut_sk_left = (
            cq.Sketch()
            .rect(cut_L, cut_W)
            .vertices("<X")
            .fillet(fillet_r)
        )
    
        # --- Apply cutouts ---
        result = (
            plate
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .placeSketch(
                cut_sk_left.moved(x=-x_off, y=y_off),
                cut_sk_right.moved(x= x_off, y=y_off),
            )
            .cutBlind(-H)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00998088/gpt_generated.stl')
