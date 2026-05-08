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
        L = 0.982759   # main rectangle length (X)
        W = 0.124138   # main rectangle width  (Y)
    
        cut_L = 0.444828  # cutout length (X)
        cut_W = W         # cutout width equals main width
    
        H = 0.827586      # extrusion height (Z)
        z_adjust = 0.077586
    
        # Base solid: create as non-centered so corners are easy to reference:
        # spans x=[0,L], y=[0,W], z=[0,H]
        base = cq.Workplane("XY").rect(L, W, centered=False).extrude(H)
    
        # Cutters: two prisms that remove the bottom-left and bottom-right corner regions
        # Each cutter spans full width in Y (0..W) and length cut_L in X.
        left_cutter = (
            cq.Workplane("XY")
            .rect(cut_L, cut_W, centered=False)  # spans x=[0,cut_L], y=[0,W]
            .extrude(H)
        )
    
        right_cutter = (
            cq.Workplane("XY", origin=(L - cut_L, 0, 0))
            .rect(cut_L, cut_W, centered=False)  # spans x=[L-cut_L, L], y=[0,W]
            .extrude(H)
        )
    
        result = base.cut(left_cutter).cut(right_cutter)
    
        # Translate to center with respect to width (Y) and adjust height (Z).
        # Since we built from y=[0,W], center in Y by shifting -W/2.
        # Also center in X for "proper" centering (common expectation) by shifting -L/2.
        result = result.translate((-L / 2.0, -W / 2.0, z_adjust))
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00984234/gpt_generated.stl')
