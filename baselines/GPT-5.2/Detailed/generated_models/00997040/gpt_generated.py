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
        L = 0.75          # base rectangle length (X direction)
        h = 0.0018        # base rectangle height (Y direction)
        s1 = 0.021        # first square side
        s2 = 0.0192       # second square side (slightly smaller)
        depth = 0.84      # extrusion depth (~20x width 0.042)
    
        # Coordinate system: sketch in XY plane, extrude along +Z.
        # Base rectangle centered on X so its centerline is x=0.
        xL = -L / 2
        xR =  L / 2
    
        # Base rectangle top is at y=h.
        y0 = 0.0
        y1 = h
    
        # First square:
        # bottom-right aligns with (xR, y1)
        # bottom-left aligns with x=0 => square spans x in [0, s1]
        # therefore xR must be s1 for perfect alignment; but L/2=0.375 != 0.021.
        # Interpreting "top right corner of the rectangle" as the rectangle's right end,
        # we place the square so its bottom-right is at (xR, y1), hence it spans
        # x in [xR - s1, xR]. This also makes its bottom-left lie on a vertical line
        # through the rectangle center only if xR - s1 == 0; since dimensions conflict,
        # we prioritize the explicit corner alignment at the rectangle's top-right.
        #
        # To still respect the "centerline" intent, we instead define the rectangle
        # with its centerline at x = xR - s1 (so the square's bottom-left is on it).
        # That means shifting the base rectangle so its center is at x = xR - s1.
        # Implement by redefining xL/xR accordingly.
        #
        # This yields a consistent closed profile with the described alignments.
        x_centerline = 0.0
        # enforce: square1 bottom-left x == centerline, square1 bottom-right x == rect right x
        # => rect right x = centerline + s1
        xR = x_centerline + s1
        xL = xR - L
    
        # Now square1 spans [0, s1] in x, and its bottom-right is at (xR, y1)
        sq1_x0, sq1_x1 = x_centerline, x_centerline + s1
        sq1_y0, sq1_y1 = y1, y1 + s1
    
        # Second square: bottom-right aligns with top-right of first square (sq1_x1, sq1_y1)
        sq2_x1 = sq1_x1
        sq2_x0 = sq2_x1 - s2
        sq2_y0 = sq1_y1
        sq2_y1 = sq2_y0 + s2
    
        # Trace the outer boundary (counter-clockwise) of the union shape:
        # Start at bottom-left of base rectangle, go around, including the stepped tower on the right.
        pts = [
            (xL, y0),          # base bottom-left
            (xR, y0),          # base bottom-right
            (xR, y1),          # base top-right (also sq1 bottom-right)
            (sq1_x1, sq1_y1),  # sq1 top-right
            (sq2_x1, sq2_y1),  # sq2 top-right
            (sq2_x0, sq2_y1),  # sq2 top-left
            (sq2_x0, sq2_y0),  # sq2 bottom-left (on top of sq1)
            (sq1_x0, sq2_y0),  # sq1 top-left
            (sq1_x0, y1),      # sq1 bottom-left (on base top)
            (xL, y1),          # base top-left
        ]
    
        profile = (
            cq.Workplane("XY")
            .moveTo(*pts[0])
            .lineTo(*pts[1])
            .lineTo(*pts[2])
            .lineTo(*pts[3])
            .lineTo(*pts[4])
            .lineTo(*pts[5])
            .lineTo(*pts[6])
            .lineTo(*pts[7])
            .lineTo(*pts[8])
            .lineTo(*pts[9])
            .close()
        )
    
        solid = profile.extrude(depth)
        return solid
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00997040/gpt_generated.stl')
