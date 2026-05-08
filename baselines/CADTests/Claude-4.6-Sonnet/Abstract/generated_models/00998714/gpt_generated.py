import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        s = 60.0          # side length of equilateral triangle
        h = s * math.sqrt(3) / 2   # height of equilateral triangle (~51.96)
        r = s / 3.0       # radius of semicircle (diameter = 2s/3 = 40mm)
        depth = 20.0      # extrusion depth
    
        # --- Triangle vertices (pointing downward) ---
        # Place top edge at y=0, apex pointing down at y=-h
        # Top-left:  (-s/2,  0)
        # Top-right: ( s/2,  0)
        # Apex:      (  0,  -h)
        apex_x = 0.0
        apex_y = -h
        tl_x, tl_y = -s/2, 0.0
        tr_x, tr_y =  s/2, 0.0
    
        # --- Step 1: Create the full equilateral triangle and extrude ---
        triangle = (
            cq.Workplane("XY")
            .moveTo(tl_x, tl_y)
            .lineTo(tr_x, tr_y)
            .lineTo(apex_x, apex_y)
            .close()
            .extrude(depth)
        )
    
        # --- Step 2: Create a cylinder centered at the apex for boolean cut ---
        # The interior angle at the apex of an equilateral triangle is 60°.
        # A full cylinder centered at the apex will intersect the triangle solid
        # in a 60° sector. This gives the semicircular-like cutout at the corner.
        cutter = (
            cq.Workplane("XY")
            .moveTo(apex_x, apex_y)
            .circle(r)
            .extrude(depth)
        )
    
        # --- Step 3: Boolean subtract ---
        result = triangle.cut(cutter)
    
        # --- Final object verification ---
        TOL = 0.5
    
        bb = result.val().BoundingBox()
    
        # X extent: from -s/2 to s/2 = s
        assert abs(bb.xlen - s) < TOL, \
            f"X length: expected {s}, got {bb.xlen}"
    
        # Y extent: from apex_y=-h to top_y=0, so ylen = h
        expected_ylen = h
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.3f}, got {bb.ylen:.3f}"
    
        # Z extent: extrusion depth
        assert abs(bb.zlen - depth) < TOL, \
            f"Z length: expected {depth}, got {bb.zlen}"
    
        # Volume: triangle area minus 60° sector area (interior angle at apex = 60°)
        triangle_area = (math.sqrt(3) / 4) * s**2
        sector_area = (60.0 / 360.0) * math.pi * r**2
        expected_vol = (triangle_area - sector_area) * depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check that a point inside the cutout (60° sector at apex) is outside the solid
        # The bisector of the apex angle points straight up (+Y from apex).
        # A point at distance r/2 from apex along the bisector should be in the cutout.
        test_cutout = (apex_x, apex_y + r/2, depth/2)
        assert not result.val().isInside(test_cutout), \
            f"Point {test_cutout} should be outside (in cutout region)"
    
        # A point well inside the triangle body (near top center) should be inside
        test_body = (0.0, -5.0, depth/2)
        assert result.val().isInside(test_body), \
            f"Point {test_body} should be inside the solid"
    
        # Face count:
        # 2 flat end faces (Z=0 and Z=depth)
        # 3 planar side faces (triangle sides)
        # 1 cylindrical face (from the circular cutout)
        # Total = 6
        n_faces = result.faces().size()
        assert n_faces == 6, f"Face count: expected 6, got {n_faces}"
    
        n_cyl = result.faces("%Cylinder").size()
        assert n_cyl == 1, f"Cylindrical faces: expected 1, got {n_cyl}"
    
        n_planar = result.faces("%Plane").size()
        assert n_planar == 5, f"Planar faces: expected 5, got {n_planar}"
    
        # Bounding box center X should be ~0 (symmetric)
        bb_center_x = (bb.xmin + bb.xmax) / 2
        assert abs(bb_center_x) < TOL, \
            f"BBox center X: expected ~0, got {bb_center_x:.3f}"
    
        print(f"All assertions passed!")
        print(f"  Side: {s} mm, r: {r:.2f} mm, depth: {depth} mm")
        print(f"  Triangle area: {triangle_area:.2f}, Sector area (60°): {sector_area:.2f}")
        print(f"  Expected volume: {expected_vol:.2f}, Actual volume: {actual_vol:.2f}")
        print(f"  BBox: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Faces: {n_faces} ({n_cyl} cyl, {n_planar} planar)")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00998714/gpt_generated.stl')
