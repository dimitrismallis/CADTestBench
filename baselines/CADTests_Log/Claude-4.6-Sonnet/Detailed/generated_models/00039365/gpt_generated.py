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
        # --- Step 1: Define parallelogram vertices ---
        # Points: [(0.6147, 0), (1.500795, 0), (0.886095, 0.354438), (0, 0.354438)]
        # Order them for a proper closed polygon (CCW):
        # Bottom-left: (0.6147, 0)
        # Bottom-right: (1.500795, 0)
        # Top-right: (0.886095, 0.354438)
        # Top-left: (0, 0.354438)
    
        p1 = (0.6147, 0)
        p2 = (1.500795, 0)
        p3 = (0.886095, 0.354438)
        p4 = (0, 0.354438)
    
        # --- Step 2: Create the parallelogram profile and extrude ---
        extrude_height = 0.425326
    
        # Build the parallelogram as a closed wire using lineTo
        result = (
            cq.Workplane("XY")
            .moveTo(p1[0], p1[1])
            .lineTo(p2[0], p2[1])
            .lineTo(p3[0], p3[1])
            .lineTo(p4[0], p4[1])
            .close()
            .extrude(extrude_height)
        )
    
        # --- Step 3: Compute center of parallelogram for hole placement ---
        # Centroid of the four vertices
        cx = (p1[0] + p2[0] + p3[0] + p4[0]) / 4.0
        cy = (p1[1] + p2[1] + p3[1] + p4[1]) / 4.0
        # cx = (0.6147 + 1.500795 + 0.886095 + 0) / 4 = 3.001590 / 4 = 0.750398
        # cy = (0 + 0 + 0.354438 + 0.354438) / 4 = 0.177219
    
        sq_w = 0.306589
        sq_h = 0.25874
    
        # --- Step 4: Cut the square hole through the full height ---
        # Work on the top face, cut through all
        result = (
            result
            .faces(">Z")
            .workplane()
            .center(cx, cy)
            .rect(sq_w, sq_h)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Check bounding box
        bb = result.val().BoundingBox()
    
        # X range: from 0 (leftmost top point) to 1.500795 (rightmost bottom point)
        assert abs(bb.xmin - 0.0) < TOL, f"xmin expected ~0, got {bb.xmin}"
        assert abs(bb.xmax - 1.500795) < TOL, f"xmax expected ~1.500795, got {bb.xmax}"
    
        # Y range: from 0 to 0.354438
        assert abs(bb.ymin - 0.0) < TOL, f"ymin expected ~0, got {bb.ymin}"
        assert abs(bb.ymax - 0.354438) < TOL, f"ymax expected ~0.354438, got {bb.ymax}"
    
        # Z range: from 0 to extrude_height
        assert abs(bb.zmin - 0.0) < TOL, f"zmin expected ~0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_height) < TOL, f"zmax expected ~{extrude_height}, got {bb.zmax}"
    
        # Check volume: parallelogram area * height - square hole area * height
        # Parallelogram area using shoelace formula
        pts = [p1, p2, p3, p4]
        n = len(pts)
        area_para = 0.0
        for i in range(n):
            j = (i + 1) % n
            area_para += pts[i][0] * pts[j][1]
            area_para -= pts[j][0] * pts[i][1]
        area_para = abs(area_para) / 2.0
    
        sq_area = sq_w * sq_h
        expected_vol = area_para * extrude_height - sq_area * extrude_height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that the hole exists: a point at the center of the square at mid-height
        # should be OUTSIDE the solid (it's been cut)
        mid_z = extrude_height / 2.0
        hole_center = cq.Vector(cx, cy, mid_z)
        solid = result.val()
        assert not solid.isInside(hole_center, tolerance=0.001), \
            f"Center of hole should be outside solid, but isInside returned True"
    
        # Check that a point inside the parallelogram but outside the hole is INSIDE
        # Use a point offset from center
        inside_pt = cq.Vector(cx + sq_w, cy, mid_z)
        # Make sure this point is within the parallelogram bounds
        assert solid.isInside(inside_pt, tolerance=0.001), \
            f"Point inside parallelogram should be inside solid"
    
        # Check cylindrical faces for the hole (should be 0 - it's a rectangular hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces (rectangular hole), got {cyl_faces}"
    
        # The hole creates 4 inner rectangular faces + top/bottom faces with hole cutout
        # Total planar faces: 4 (parallelogram sides) + 2 (top/bottom with hole) + 4 (hole walls) = 10
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 8, f"Expected at least 8 planar faces, got {planar_faces}"
    
        print(f"Parallelogram area: {area_para:.6f}")
        print(f"Square hole area: {sq_area:.6f}")
        print(f"Expected volume: {expected_vol:.6f}")
        print(f"Actual volume: {actual_vol:.6f}")
        print(f"Centroid: ({cx:.6f}, {cy:.6f})")
        print(f"Bounding box: X[{bb.xmin:.4f}, {bb.xmax:.4f}] Y[{bb.ymin:.4f}, {bb.ymax:.4f}] Z[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Planar faces: {planar_faces}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00039365/gpt_generated.stl')
