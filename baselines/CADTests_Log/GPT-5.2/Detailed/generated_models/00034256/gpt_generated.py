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
        # Parameters (CadQuery default units: mm; treat "units" as mm here)
        L = 0.75          # base length (X)
        W = 0.30          # U outer width (Y)
        base_h = 0.15     # base thickness
        total_h = 0.45    # total height at the clamping legs
        extra_h = total_h - base_h
    
        wall = 0.06       # U wall thickness
        leg_depth = 0.45  # depth of the U opening region from the open end (in X)
    
        close_extra_w = 0.45
        close_w = W + close_extra_w
        close_len = wall  # closing bar thickness along X
    
        # Derived inner cutout size (ensure valid)
        inner_len = max(leg_depth - wall, 0.001)
        inner_w = max(W - 2 * wall, 0.001)
    
        # --- Base solid: outer block extruded, then cut inner pocket to form U, then add closing bar ---
        # Outer base block: X from 0..L, Y centered, Z from 0..base_h
        base = (
            cq.Workplane("XY")
            .center(L / 2.0, 0.0)
            .rect(L, W)
            .extrude(base_h)
        )
    
        # Cut inner pocket in the open-end region to create the U void
        # Pocket spans X: [L-leg_depth+wall, L-wall] approximately, leaving a wall at the open end too.
        pocket = (
            cq.Workplane("XY")
            .center(L - leg_depth + wall + inner_len / 2.0, 0.0)
            .rect(inner_len, inner_w)
            .extrude(base_h)
        )
        base = base.cut(pocket)
    
        # Closing bar at the open end, wider than U by 0.45 in Y
        closing_bar = (
            cq.Workplane("XY")
            .center(L - close_len / 2.0, 0.0)
            .rect(close_len, close_w)
            .extrude(base_h)
        )
        base = base.union(closing_bar)
    
        # --- Taller legs: add material on top of base for the two side walls in the open region ---
        leg_len_x = leg_depth
        leg_w_y = wall
    
        legs = (
            cq.Workplane("XY", origin=(0, 0, base_h))
            .pushPoints([
                (L - leg_depth / 2.0, -W / 2.0 + wall / 2.0),
                (L - leg_depth / 2.0,  W / 2.0 - wall / 2.0),
            ])
            .rect(leg_len_x, leg_w_y)
            .extrude(extra_h)
        )
    
        final_result = base.union(legs)
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00034256/gpt_generated.stl')
