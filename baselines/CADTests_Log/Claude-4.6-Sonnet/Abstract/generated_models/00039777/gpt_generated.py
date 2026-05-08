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
        # --- Step 1: Define pentagon vertices (flat bottom orientation) ---
        # Regular pentagon with flat bottom: vertices at angles 90+36+72k = 54, 126, 198, 270, 342
        # Wait - for flat bottom we need a horizontal bottom EDGE (two vertices at bottom).
        # Use angles: 18, 90, 162, 234, 306 degrees (starting from right, CCW)
        # This gives: right(18°), top(90°), left(162°), bottom-left(234°), bottom-right(306°)
        # Bottom edge: bottom-left(234°) to bottom-right(306°) — horizontal? 
        # sin(234°) = sin(306°) = -sin(54°) ≈ -0.809 ✓ same Y → flat bottom edge!
    
        R = 20.0  # circumradius
        angles_deg = [18, 90, 162, 234, 306]  # CCW order
    
        # Pentagon vertices (CCW from right)
        penta = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a))) for a in angles_deg]
        # penta[0] = right (18°)
        # penta[1] = top (90°)
        # penta[2] = left (162°)
        # penta[3] = bottom-left (234°)
        # penta[4] = bottom-right (306°)
    
        # The two "top edges" of the pentagon (with flat bottom) are:
        #   Edge A: penta[0] (right) → penta[1] (top)
        #   Edge B: penta[1] (top)   → penta[2] (left)
    
        # --- Step 2: Insert a slightly-displaced midpoint on each top edge ---
        # The displacement creates an obtuse angle very close to 180°.
        # We displace the midpoint INWARD (toward center) by a small amount d.
        # The angle at the new vertex: if edge length = L and displacement = d,
        # then half-angle from 180° ≈ arctan(2d/L) * 2 (small angle approx).
        # For ~175°, we need deviation of 2.5° → d ≈ L/2 * tan(2.5°) ≈ L * 0.0218
    
        def insert_midpoint_inward(p1, p2, inward_fraction=0.022):
            """Insert a midpoint displaced inward (toward origin) from the edge midpoint."""
            mx = (p1[0] + p2[0]) / 2.0
            my = (p1[1] + p2[1]) / 2.0
            # Edge vector and length
            ex = p2[0] - p1[0]
            ey = p2[1] - p1[1]
            L = math.sqrt(ex**2 + ey**2)
            # Inward normal (rotate edge vector 90° CCW, then normalize, pointing toward center for CCW polygon)
            # For CCW polygon, inward normal is the left normal of the edge direction
            nx = -ey / L
            ny = ex / L
            # Check if this points toward origin (center)
            # dot with (mx, my) should be negative if pointing inward
            dot = nx * mx + ny * my
            if dot > 0:
                nx, ny = -nx, -ny
            d = inward_fraction * L
            return (mx + nx * d, my + ny * d)
    
        # Edge A: penta[0] → penta[1]
        mid_A = insert_midpoint_inward(penta[0], penta[1])
        # Edge B: penta[1] → penta[2]
        mid_B = insert_midpoint_inward(penta[1], penta[2])
    
        # --- Step 3: Build the 7-vertex polygon (CCW order) ---
        # Original CCW: p0, p1, p2, p3, p4
        # Insert mid_A between p0 and p1, mid_B between p1 and p2
        polygon_pts = [
            penta[0],   # right
            mid_A,      # midpoint on right-top edge (slightly inward)
            penta[1],   # top
            mid_B,      # midpoint on left-top edge (slightly inward)
            penta[2],   # left
            penta[3],   # bottom-left
            penta[4],   # bottom-right
        ]
    
        # --- Step 4: Extrude the polygon ---
        extrude_height = 15.0
    
        # Build the polygon using lineTo
        wp = cq.Workplane("XY")
        wp = wp.moveTo(polygon_pts[0][0], polygon_pts[0][1])
        for pt in polygon_pts[1:]:
            wp = wp.lineTo(pt[0], pt[1])
        wp = wp.close()
        result = wp.extrude(extrude_height)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Check bounding box
        bb = result.val().BoundingBox()
    
        # X extent: from bottom-right (306°) to bottom-left (234°) or right (18°) to left (162°)
        x_right = R * math.cos(math.radians(18))   # ≈ 19.02
        x_left  = R * math.cos(math.radians(162))  # ≈ -19.02
        expected_xlen = x_right - x_left
        assert abs(bb.xlen - expected_xlen) < TOL, f"X extent: expected {expected_xlen:.3f}, got {bb.xlen:.3f}"
    
        # Y extent: from bottom (sin(234°)*R) to top (sin(90°)*R = R)
        y_top    = R * math.sin(math.radians(90))   # = 20.0
        y_bottom = R * math.sin(math.radians(234))  # ≈ -16.18
        expected_ylen = y_top - y_bottom
        assert abs(bb.ylen - expected_ylen) < TOL, f"Y extent: expected {expected_ylen:.3f}, got {bb.ylen:.3f}"
    
        # Z extent: extrude height
        assert abs(bb.zlen - extrude_height) < TOL, f"Z extent: expected {extrude_height}, got {bb.zlen:.3f}"
    
        # Check face count: 
        # Bottom face: 1 (heptagon)
        # Top face: 1 (heptagon)
        # Side faces: 7 (one per edge of the heptagon)
        # Total: 9 faces
        n_faces = result.faces().size()
        assert n_faces == 9, f"Face count: expected 9, got {n_faces}"
    
        # Check edge count:
        # Top: 7 edges, Bottom: 7 edges, Vertical: 7 edges → 21 total
        n_edges = result.edges().size()
        assert n_edges == 21, f"Edge count: expected 21, got {n_edges}"
    
        # Check vertex count: 7 top + 7 bottom = 14
        n_verts = result.vertices().size()
        assert n_verts == 14, f"Vertex count: expected 14, got {n_verts}"
    
        # Check volume: area of heptagon * height
        # Compute polygon area using shoelace formula
        pts = polygon_pts
        n = len(pts)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += pts[i][0] * pts[j][1]
            area -= pts[j][0] * pts[i][1]
        area = abs(area) / 2.0
        expected_vol = area * extrude_height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Verify the two inserted midpoints create obtuse angles close to 180°
        def angle_at_vertex(p_prev, p_mid, p_next):
            """Compute interior angle at p_mid in degrees."""
            v1 = (p_prev[0] - p_mid[0], p_prev[1] - p_mid[1])
            v2 = (p_next[0] - p_mid[0], p_next[1] - p_mid[1])
            dot = v1[0]*v2[0] + v1[1]*v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            cos_a = max(-1.0, min(1.0, dot / (mag1 * mag2)))
            return math.degrees(math.acos(cos_a))
    
        angle_A = angle_at_vertex(penta[0], mid_A, penta[1])
        angle_B = angle_at_vertex(penta[1], mid_B, penta[2])
    
        assert 170 < angle_A < 180, f"Angle at mid_A: expected 170-180°, got {angle_A:.2f}°"
        assert 170 < angle_B < 180, f"Angle at mid_B: expected 170-180°, got {angle_B:.2f}°"
    
        print(f"Angle at mid_A (on right-top edge): {angle_A:.2f}°")
        print(f"Angle at mid_B (on left-top edge):  {angle_B:.2f}°")
        print(f"Polygon area: {area:.4f} mm²")
        print(f"Volume: {actual_vol:.4f} mm³")
        print(f"Bounding box: X={bb.xlen:.3f}, Y={bb.ylen:.3f}, Z={bb.zlen:.3f}")
        print(f"Faces: {n_faces}, Edges: {n_edges}, Vertices: {n_verts}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00039777/gpt_generated.stl')
