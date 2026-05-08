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
        outer_w = 40.0          # overall U outer width (X)
        outer_h = 30.0          # overall U outer height (Y)
        wall = 6.0              # U wall thickness
        bottom_fill_h = 10.0    # "fill in the empty space" height from the bottom inside the U
        cap_w = 60.0            # closing rectangle width (wider than U)
        cap_h = 8.0             # closing rectangle height
        thickness = 12.0        # extrusion thickness (Z)
    
        # Derived inner opening size (inner void is shifted upward to leave bottom wall)
        inner_w = outer_w - 2 * wall
        inner_h = outer_h - wall
    
        # Centers in Y for inner void, bottom fill, and cap
        inner_void_cy = wall / 2.0
        bottom_fill_cy = -outer_h / 2.0 + wall + bottom_fill_h / 2.0
        cap_cy = outer_h / 2.0 + cap_h / 2.0
    
        # --- Build 2D sketch with proper boolean modes ---
        sk = (
            cq.Sketch()
            # Outer boundary
            .rect(outer_w, outer_h, mode="a")
            # Subtract inner void to make the U
            .push([(0, inner_void_cy)])
            .rect(inner_w, inner_h, mode="s")
            # Fill the empty space inside the U (add material back at the bottom)
            .push([(0, bottom_fill_cy)])
            .rect(inner_w, bottom_fill_h, mode="a")
            # Close the open part with a wider top cap
            .push([(0, cap_cy)])
            .rect(cap_w, cap_h, mode="a")
        )
    
        result = cq.Workplane("XY").placeSketch(sk).extrude(thickness)
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00034256/gpt_generated.stl')
