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
        length = 0.75
        width = 0.340821
        height = 0.031444
    
        right_margin = 0.16366
        left_margin = 0.117823
    
        offset = 0.047166  # inward offset for the hole
    
        # --- Outer trapezoid geometry (in XY) ---
        # Define trapezoid with bottom edge spanning full length at y=-width/2
        # and top edge shortened by left/right margins at y=+width/2.
        yb = -width / 2.0
        yt =  width / 2.0
    
        p1 = (0.0, yb)                          # bottom-left
        p2 = (length, yb)                       # bottom-right
        p3 = (length - right_margin, yt)        # top-right
        p4 = (left_margin, yt)                  # top-left
    
        # --- Inner trapezoid (offset inward by 'offset') ---
        # For horizontal edges: move in by offset in Y and shrink in X by offset on both ends.
        # For slanted edges: move the intersection points inward by offset along the edge normals.
        # A robust/simple approach here: compute inner points by intersecting lines offset inward.
        #
        # We'll offset each of the 4 boundary lines inward by distance=offset and intersect them.
    
        def offset_line_inward(pA, pB, inward_ref, d):
            """
            Return (n, c) for the offset line in form n·(x,y)=c, where n is unit normal.
            The line through pA->pB is offset by distance d toward inward_ref point.
            """
            ax, ay = pA
            bx, by = pB
            dx, dy = (bx - ax), (by - ay)
    
            # Two candidate unit normals
            # n1 = ( -dy, dx ) normalized, n2 = -n1
            L = math.hypot(dx, dy)
            n1 = (-dy / L, dx / L)
            n2 = (dy / L, -dx / L)
    
            # Choose normal that points toward inward_ref (i.e., inward_ref is on positive side)
            # For line n·x = c, points with n·x > c are on the normal side.
            c0_1 = n1[0] * ax + n1[1] * ay
            c0_2 = n2[0] * ax + n2[1] * ay
    
            s1 = (n1[0] * inward_ref[0] + n1[1] * inward_ref[1]) - c0_1
            s2 = (n2[0] * inward_ref[0] + n2[1] * inward_ref[1]) - c0_2
    
            if s1 >= 0:
                n = n1
                c0 = c0_1
            else:
                n = n2
                c0 = c0_2
    
            # Offset inward: move line along +n by distance d => c = c0 + d
            return n, c0 + d
    
        def intersect_lines(nc1, nc2):
            (n1, c1) = nc1
            (n2, c2) = nc2
            a11, a12 = n1
            a21, a22 = n2
            det = a11 * a22 - a12 * a21
            if abs(det) < 1e-12:
                raise ValueError("Lines are parallel; cannot intersect.")
            x = (c1 * a22 - a12 * c2) / det
            y = (a11 * c2 - c1 * a21) / det
            return (x, y)
    
        # Inward reference point: centroid-ish of outer trapezoid
        inward_ref = ((p1[0] + p2[0] + p3[0] + p4[0]) / 4.0, (p1[1] + p2[1] + p3[1] + p4[1]) / 4.0)
    
        # Define boundary edges in CCW order: p1->p2->p3->p4->p1
        e12 = (p1, p2)
        e23 = (p2, p3)
        e34 = (p3, p4)
        e41 = (p4, p1)
    
        # Offset each edge inward
        L12 = offset_line_inward(*e12, inward_ref=inward_ref, d=offset)
        L23 = offset_line_inward(*e23, inward_ref=inward_ref, d=offset)
        L34 = offset_line_inward(*e34, inward_ref=inward_ref, d=offset)
        L41 = offset_line_inward(*e41, inward_ref=inward_ref, d=offset)
    
        # Intersections give inner polygon vertices (same order)
        q1 = intersect_lines(L41, L12)  # near p1
        q2 = intersect_lines(L12, L23)  # near p2
        q3 = intersect_lines(L23, L34)  # near p3
        q4 = intersect_lines(L34, L41)  # near p4
    
        # --- Build solid and cut hole ---
        outer = (
            cq.Workplane("XY")
            .polyline([p1, p2, p3, p4])
            .close()
            .extrude(height)
        )
    
        result = (
            outer
            .faces(">Z").workplane()
            .polyline([q1, q2, q3, q4])
            .close()
            .cutThruAll()
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00985482/gpt_generated.stl')
