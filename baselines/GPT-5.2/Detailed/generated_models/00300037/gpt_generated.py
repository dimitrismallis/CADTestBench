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
        u_len = 0.75
        u_wid = 0.199115
        h = 0.165929
    
        # U-shape wall thickness (not specified; choose a reasonable value)
        wall = 0.05  # must be < u_wid/2
    
        # Bottom pads (called "squares" in prompt, but dimensions are rectangular)
        pad_x = 0.126106
        pad_y = 0.225664
    
        # Overlap amount into the U's bottom corners
        overlap = 0.01
    
        # --- Build U-shaped profile as a frame: outer rect minus inner rect ---
        # Open at the top by removing the inner rectangle that reaches the top edge.
        # Inner rectangle is shifted upward so its top coincides with outer top,
        # leaving a bottom bar thickness = wall.
        outer = cq.Workplane("XY").rect(u_len, u_wid)
        inner = (
            cq.Workplane("XY")
            .center(0, wall / 2)  # shift up so inner top aligns with outer top
            .rect(u_len - 2 * wall, u_wid - wall)
        )
    
        u_solid = outer.extrude(h).cut(inner.extrude(h))
    
        # --- Add two bottom corner pads, slightly overlapping the outer corners ---
        # Outer rectangle extents:
        x_min = -u_len / 2
        x_max =  u_len / 2
        y_min = -u_wid / 2
    
        # Place pads so they sit at bottom-left and bottom-right corners,
        # with a small overlap into the U (in +X for left pad, -X for right pad, and +Y upward).
        left_center = (
            x_min + pad_x / 2 - overlap,   # shift slightly left so it overlaps the corner
            y_min + pad_y / 2 - overlap    # shift slightly down so it overlaps the corner
        )
        right_center = (
            x_max - pad_x / 2 + overlap,   # shift slightly right so it overlaps the corner
            y_min + pad_y / 2 - overlap
        )
    
        pads = (
            cq.Workplane("XY")
            .pushPoints([left_center, right_center])
            .rect(pad_x, pad_y)
            .extrude(h)
        )
    
        result = u_solid.union(pads)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00300037/gpt_generated.stl')
