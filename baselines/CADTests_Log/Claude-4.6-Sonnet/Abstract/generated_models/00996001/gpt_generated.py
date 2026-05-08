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
        W = 50.0        # total width of the U-shape
        H = 30.0        # total height of the U-shape
        h = 5.0         # thickness of the horizontal section
        col_w = 2 * h   # column width = 10 mm (twice horizontal thickness)
        D = 40.0        # extrusion depth
        hole_d = 6.0    # diameter of the circular hole
    
        # Derived dimensions
        inner_w = W - 2 * col_w   # 30 mm - width of the inner cutout
        inner_h = H - h            # 25 mm - height of the inner cutout (column height)
    
        # --- Step 1: Create the full bounding box ---
        # The U-shape: horizontal bar on top (thickness h), two columns on sides (width col_w)
        # We build it as a full box then subtract the inner rectangular cutout
        # Oriented so the U opens downward (inverted table):
        #   - Horizontal bar spans full width W, thickness h, at the top
        #   - Two columns hang down from the bar, each col_w wide, inner_h tall
        # The object sits with its base at Z=0, extends to Z=D in depth
    
        # Full outer box: W x H x D
        result = cq.Workplane("XY").box(W, H, D)
    
        # --- Step 2: Subtract the inner rectangular cutout to form the U-shape ---
        # The cutout is centered in X, at the bottom of the shape (open bottom)
        # Cutout dimensions: inner_w x inner_h, centered in X, aligned to bottom in Y
        # In the centered box, bottom face is at Y = -H/2
        # Cutout goes from Y = -H/2 up to Y = -H/2 + inner_h = H/2 - h
        # Cutout is centered in X (x from -inner_w/2 to inner_w/2)
        # Cutout goes full depth in Z
    
        # Place a box for the cutout: centered in X, bottom-aligned in Y
        # The cutout box center in Y: -H/2 + inner_h/2 = -H/2 + (H-h)/2 = -h/2
        cutout = cq.Workplane("XY").box(inner_w, inner_h, D)
        # Move cutout so its bottom aligns with the bottom of the main box
        # Main box bottom: Y = -H/2; cutout height = inner_h
        # Cutout center Y = -H/2 + inner_h/2
        cutout_center_y = -H / 2 + inner_h / 2
        cutout = cutout.translate((0, cutout_center_y, 0))
    
        result = result.cut(cutout)
    
        # --- Step 3: Add a circular hole at the center of the horizontal surface ---
        # The horizontal surface (top face of the U, the "table surface" when inverted)
        # is the face at maximum Y (Y = H/2)
        # The hole goes through the horizontal bar (thickness h in Y direction)
        # Hole is centered at X=0, Z=0 (center of the top face)
        result = (
            result
            .faces(">Y")
            .workplane()
            .hole(hole_d)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Check bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - W) < TOL, f"X length: expected {W}, got {bb.xlen}"
        assert abs(bb.ylen - H) < TOL, f"Y length: expected {H}, got {bb.ylen}"
        assert abs(bb.zlen - D) < TOL, f"Z length: expected {D}, got {bb.zlen}"
    
        # Check volume:
        # U-shape cross-section area = W*H - inner_w*inner_h
        u_area = W * H - inner_w * inner_h
        # Hole goes through the horizontal bar only (thickness h in Y)
        hole_vol = math.pi * (hole_d / 2) ** 2 * h
        expected_vol = u_area * D - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check cylindrical face exists (the hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face (hole), got {cyl_faces}"
    
        # Check circular edges exist (hole boundary)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges >= 2, f"Expected at least 2 circular edges (hole top/bottom), got {circ_edges}"
    
        # Check the hole is centered in X and Z
        cyl_face = result.faces("%Cylinder").val()
        cyl_center = cyl_face.Center()
        assert abs(cyl_center.x) < TOL, f"Hole center X: expected 0, got {cyl_center.x}"
        assert abs(cyl_center.z) < TOL, f"Hole center Z: expected 0, got {cyl_center.z}"
    
        # Check the hole is in the horizontal bar - center Y should be near H/2 - h/2
        expected_hole_y = H / 2 - h / 2
        assert abs(cyl_center.y - expected_hole_y) < TOL, \
            f"Hole center Y: expected {expected_hole_y}, got {cyl_center.y}"
    
        # Verify the hole radius via circular edge bounding box
        circ_edge = result.edges("%Circle").val()
        edge_bb = circ_edge.BoundingBox()
        radius = edge_bb.xlen / 2
        assert abs(radius - hole_d / 2) < TOL, f"Hole radius: expected {hole_d/2}, got {radius}"
    
        # Verify the U-shape has the correct number of planar faces
        # Expected planar faces: 
        #   outer: top(1) + bottom(2 column bottoms) + front(3) + back(3) + left(1) + right(1) = 11
        #   plus 2 circular faces from hole = 13 total faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 8, f"Expected at least 8 planar faces, got {planar_faces}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f})")
        print(f"  U-shape area: {u_area:.2f} mm²")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Circular edges: {circ_edges}")
        print(f"  Planar faces: {planar_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00996001/gpt_generated.stl')
