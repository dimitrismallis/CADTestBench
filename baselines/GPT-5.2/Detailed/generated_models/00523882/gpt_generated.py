import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def right_trapezoid_prism(base_len, top_len, height, width):
        """
        Creates a right trapezoidal prism:
        - 2D trapezoid lies in XY plane
        - base is along X at y=0 from x=0..base_len
        - top is along X at y=height from x=0..top_len
        - left side is vertical (x=0), right side is slanted
        - extruded along +Z by 'width'
        """
        profile = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(base_len, 0)
            .lineTo(top_len, height)
            .lineTo(0, height)
            .close()
        )
        return profile.extrude(width)
    
    def create_cad() -> cq.Workplane:
        # --- Parameters (units as given) ---
        b1, t1, h1, w1 = 1.11043, 0.55953, 0.625913, 1.0011
        b2, t2, h2, w2 = 1.27908, 0.619642, 0.75, 0.201835
    
        # --- Build prisms ---
        p1 = right_trapezoid_prism(b1, t1, h1, w1)
        p2 = right_trapezoid_prism(b2, t2, h2, w2)
    
        # --- Attach p2 to one side of p1 ---
        # Put p2's left face (x=0) against p1's rightmost face (x=b1).
        # Also center p2 in Y relative to p1, and align bottoms (y=0).
        y_centering = (h1 - h2) / 2.0  # negative means p2 is taller, so it will extend beyond p1
        attach_translation = (b1, y_centering, 0.0)
    
        # Add a small rotation about Z to satisfy "translated and rotated" alignment.
        # Rotate around p2's left-bottom corner (its local origin) after translation.
        rot_deg = -7.5
    
        p2_attached = (
            p2
            .translate(attach_translation)
            .rotate((b1, y_centering, 0.0), (b1, y_centering, 1.0), rot_deg)
        )
    
        # Union into a single model
        result = p1.union(p2_attached)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00523882/gpt_generated.stl')
