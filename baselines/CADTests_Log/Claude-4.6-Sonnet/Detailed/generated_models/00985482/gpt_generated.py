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
        # --- Parameters ---
        length = 0.75
        width = 0.340821
        height = 0.031444
        right_margin = 0.16366
        left_margin = 0.117823
        offset_dist = 0.047166
    
        # --- Step 1: Define outer trapezoid vertices ---
        half_len = length / 2.0
        half_wid = width / 2.0
    
        # Vertices: bottom-left, bottom-right, top-right, top-left
        bl = (-half_len, -half_wid)
        br = (half_len, -half_wid)
        tr = (half_len - right_margin, half_wid)
        tl = (-half_len + left_margin, half_wid)
    
        outer_pts = [bl, br, tr, tl]
    
        # --- Step 2: Compute inner trapezoid by offsetting each edge inward ---
        # We compute the inward offset of each edge line, then find intersections.
        # 
        # For each edge, compute the unit inward normal, then offset the line.
        # "Inward" means toward the interior of the polygon.
        # We determine inward direction by checking which side the centroid is on.
    
        def line_offset(p1, p2, d):
            """
            Return the offset line (as point + direction) of edge p1->p2,
            offset by d in the direction of the inward normal.
            The inward normal is determined by the centroid of the polygon.
            Returns (offset_p1, offset_p2) — two points on the offset line.
            """
            p1 = np.array(p1, dtype=float)
            p2 = np.array(p2, dtype=float)
            edge = p2 - p1
            edge_len = np.linalg.norm(edge)
            # Two candidate normals
            n1 = np.array([-edge[1], edge[0]]) / edge_len   # rotate CCW
            n2 = np.array([edge[1], -edge[0]]) / edge_len   # rotate CW
            return n1, n2, p1, p2
    
        def line_intersect(p1, d1, p2, d2):
            """Find intersection of two lines: p1 + t*d1 = p2 + s*d2"""
            A = np.array([[d1[0], -d2[0]], [d1[1], -d2[1]]])
            b = p2 - p1
            try:
                ts = np.linalg.solve(A, b)
                return p1 + ts[0] * d1
            except np.linalg.LinAlgError:
                return p1
    
        def offset_polygon_inward(pts, d):
            """
            Offset polygon inward by distance d.
            Uses centroid to determine inward direction for each edge.
            """
            n = len(pts)
            pts_arr = [np.array(p, dtype=float) for p in pts]
    
            # Compute centroid
            cx = sum(p[0] for p in pts) / n
            cy = sum(p[1] for p in pts) / n
            centroid = np.array([cx, cy])
    
            # For each edge, compute the inward normal
            inward_normals = []
            edges_dir = []
            for i in range(n):
                p1 = pts_arr[i]
                p2 = pts_arr[(i + 1) % n]
                edge = p2 - p1
                edge_len = np.linalg.norm(edge)
                edge_dir = edge / edge_len
    
                # Two candidate normals
                n1 = np.array([-edge[1], edge[0]]) / edge_len   # rotate CCW
                n2 = np.array([edge[1], -edge[0]]) / edge_len   # rotate CW
    
                # Edge midpoint
                mid = (p1 + p2) / 2.0
    
                # The inward normal points toward the centroid
                # Check which normal has positive dot product with (centroid - mid)
                to_centroid = centroid - mid
                if np.dot(n1, to_centroid) > 0:
                    inward_normals.append(n1)
                else:
                    inward_normals.append(n2)
                edges_dir.append(edge_dir)
    
            # Offset each edge and find intersections
            offset_pts = []
            for i in range(n):
                prev_i = (i - 1) % n
    
                # Offset line for edge i: starts at pts[i] + d*inward_normals[i]
                p1_off = pts_arr[i] + d * inward_normals[i]
                d1 = edges_dir[i]
    
                # Offset line for edge prev_i: starts at pts[prev_i] + d*inward_normals[prev_i]
                p2_off = pts_arr[prev_i] + d * inward_normals[prev_i]
                d2 = edges_dir[prev_i]
    
                pt = line_intersect(p1_off, d1, p2_off, d2)
                offset_pts.append((float(pt[0]), float(pt[1])))
    
            return offset_pts
    
        inner_pts = offset_polygon_inward(outer_pts, offset_dist)
    
        print(f"Outer pts: {outer_pts}")
        print(f"Inner pts: {inner_pts}")
    
        def signed_area(pts):
            n = len(pts)
            area = 0.0
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                area += (x1 * y2 - x2 * y1)
            return area / 2.0
    
        def polygon_area(pts):
            return abs(signed_area(pts))
    
        outer_area = polygon_area(outer_pts)
        inner_area = polygon_area(inner_pts)
        print(f"Outer area: {outer_area:.6f}, Inner area: {inner_area:.6f}")
    
        # Sanity check: inner polygon must be smaller
        assert inner_area < outer_area, \
            f"Inner area {inner_area:.6f} should be smaller than outer area {outer_area:.6f}"
    
        # --- Step 3: Build outer trapezoid solid ---
        outer_sketch = cq.Sketch().polygon(outer_pts)
        result = (
            cq.Workplane("XY")
            .placeSketch(outer_sketch)
            .extrude(height)
        )
    
        # --- Step 4: Build inner trapezoid solid and cut through ---
        inner_sketch = cq.Sketch().polygon(inner_pts)
        inner_solid = (
            cq.Workplane("XY")
            .placeSketch(inner_sketch)
            .extrude(height)
        )
    
        result = result.cut(inner_solid)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Check bounding box matches outer trapezoid dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, \
            f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width) < TOL, \
            f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z height: expected {height}, got {bb.zlen}"
    
        # Check volume = (outer_area - inner_area) * height
        expected_vol = (outer_area - inner_area) * height
        actual_vol = result.val().Volume()
    
        print(f"Expected volume: {expected_vol:.6f}, Actual volume: {actual_vol:.6f}")
    
        assert actual_vol > 0, \
            f"Volume should be positive, got {actual_vol}"
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume mismatch: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check planar faces: 4 outer sides + 4 inner sides + top ring + bottom ring = 10
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 8, \
            f"Expected at least 8 planar faces, got {planar_faces}"
    
        # Check exactly 1 solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Check COM Z is at height/2 (symmetric extrusion)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.z - height / 2.0) < TOL, \
            f"COM Z: expected {height/2.0:.6f}, got {com.z:.6f}"
    
        # Verify hole: centroid of inner trapezoid should be OUTSIDE the solid
        inner_cx = sum(p[0] for p in inner_pts) / len(inner_pts)
        inner_cy = sum(p[1] for p in inner_pts) / len(inner_pts)
        hole_point = (inner_cx, inner_cy, height / 2.0)
        is_inside = result.val().isInside(hole_point)
        assert not is_inside, \
            f"Hole center {hole_point} should be outside solid (in hole), but isInside={is_inside}"
    
        # Verify wall material: midpoint between outer and inner bottom edges should be INSIDE solid
        outer_bottom_mid_x = (outer_pts[0][0] + outer_pts[1][0]) / 2.0
        outer_bottom_mid_y = outer_pts[0][1]
        inner_bottom_mid_x = (inner_pts[0][0] + inner_pts[1][0]) / 2.0
        inner_bottom_mid_y = inner_pts[0][1]
        wall_x = (outer_bottom_mid_x + inner_bottom_mid_x) / 2.0
        wall_y = (outer_bottom_mid_y + inner_bottom_mid_y) / 2.0
        wall_point = (wall_x, wall_y, height / 2.0)
        is_wall_inside = result.val().isInside(wall_point)
        assert is_wall_inside, \
            f"Wall point {wall_point} should be inside solid, but isInside={is_wall_inside}"
    
        # Verify top and bottom faces exist
        top_faces = result.faces(">Z").size()
        assert top_faces >= 1, f"Expected at least 1 top face, got {top_faces}"
        bot_faces = result.faces("<Z").size()
        assert bot_faces >= 1, f"Expected at least 1 bottom face, got {bot_faces}"
    
        print(f"Planar faces: {planar_faces}")
        print(f"COM: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00985482/gpt_generated.stl')
