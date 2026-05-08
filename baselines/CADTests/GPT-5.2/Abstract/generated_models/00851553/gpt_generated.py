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
        top_w = 40.0                 # width of bench top (Y)
        top_l = 3.0 * top_w          # length of bench top (X)
        top_h = top_w                # "depth" (thickness/height in Z) equals width
    
        wall = 3.0                   # shell thickness for hollow top
    
        leg_w = 14.0                 # leg width (Y)
        leg_l = 3.0 * leg_w          # leg length (X) ~ 3x width
        leg_h = 70.0                 # leg height (Z)
    
        rod_d = leg_w * 0.9          # marginally less than leg width
        rod_z = 10.0                 # height of rod center above floor
    
        # --- Bench top: hollow box ---
        top = (
            cq.Workplane("XY")
            .box(top_l, top_w, top_h, centered=(True, True, False))  # bottom at Z=0
            .faces(">Z")
            .shell(-wall)  # hollow from the top opening
        )
    
        # --- Legs: two rectangular prisms under left/right ends of the top ---
        # Place legs so their top touches the underside of the top (Z=0 plane),
        # and they extend downward.
        x_leg = (top_l / 2.0) - (leg_l / 2.0)  # centered near each end
        legs = (
            cq.Workplane("XY")
            .pushPoints([(-x_leg, 0.0), (x_leg, 0.0)])
            .rect(leg_l, leg_w)
            .extrude(-leg_h)  # downwards
        )
    
        bench = top.union(legs)
    
        # --- Rod connecting the legs near their bottoms ---
        # Span between inner faces of legs, with a small clearance.
        inner_gap = (2.0 * x_leg) - leg_l  # distance between inner faces
        rod_len = max(1.0, inner_gap - 2.0)  # small clearance
    
        rod = (
            cq.Workplane("YZ", origin=(0, 0, -leg_h + rod_z))
            .circle(rod_d / 2.0)
            .extrude(rod_len, both=True)  # along X, centered at X=0
        )
    
        bench = bench.union(rod)
    
        return bench
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00851553/gpt_generated.stl')
