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
        main_size = 50.0      # main square side length
        main_height = 20.0    # extrusion height of main square
        small_size = main_size / 5.0  # = 10.0, 1/5th of main
    
        # --- Step 1: Main square extruded along Z ---
        # Centered at origin: corners at (±25, ±25, 0..20)
        result = cq.Workplane("XY").rect(main_size, main_size).extrude(main_height)
    
        # --- Step 2 & 3: Small square at top-right corner, negative extrude ---
        # Main square top-right corner: (25, 25)
        # Small square top-right corner must also be at (25, 25)
        # Small square is 10×10, so its center is at (25 - 5, 25 - 5) = (20, 20)
        small_center_x = (main_size / 2) - (small_size / 2)  # = 20
        small_center_y = (main_size / 2) - (small_size / 2)  # = 20
    
        result = (
            result
            .faces(">Z")
            .workplane()
            .center(small_center_x, small_center_y)
            .rect(small_size, small_size)
            .cutBlind(-main_height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box: should still be 50 x 50 x 20 (cut is inside the solid)
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - main_size) < TOL, f"X length: expected {main_size}, got {bb.xlen}"
        assert abs(bb.ylen - main_size) < TOL, f"Y length: expected {main_size}, got {bb.ylen}"
        assert abs(bb.zlen - main_height) < TOL, f"Z length: expected {main_height}, got {bb.zlen}"
    
        # Volume: main box minus the small cutout
        main_vol = main_size * main_size * main_height          # 50*50*20 = 50000
        cut_vol  = small_size * small_size * main_height        # 10*10*20 = 2000
        expected_vol = main_vol - cut_vol                       # 48000
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.1f}, got {actual_vol:.1f}"
    
        # The cut should create cylindrical-free geometry — all faces should be planar
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Check that the top-right corner of the cut aligns with the top-right corner of the main solid
        # Point just inside the cut region (top-right corner area) should NOT be inside the solid
        # The cut occupies x in [15, 25], y in [15, 25], z in [0, 20]
        # A point at (22, 22, 10) should be outside (inside the cut)
        cut_interior_point = cq.Vector(22, 22, 10)
        assert not result.val().isInside(cut_interior_point), \
            f"Point {cut_interior_point} should be outside (in the cut region)"
    
        # A point at (0, 0, 10) should be inside the solid (center of main body)
        center_point = cq.Vector(0, 0, 10)
        assert result.val().isInside(center_point), \
            f"Point {center_point} should be inside the solid"
    
        # A point at (20, -10, 10) should be inside (bottom-right area, not cut)
        inside_point2 = cq.Vector(20, -10, 10)
        assert result.val().isInside(inside_point2), \
            f"Point {inside_point2} should be inside the solid"
    
        # Count planar faces: 
        # Original box has 6 faces. The cut adds:
        # - removes part of top face (top face now has a rectangular hole → becomes an L-shape, still 1 face? No, it's a face with inner wire)
        # - adds 3 new side walls of the cut (the 4th side of the cut coincides with 2 existing faces)
        # Actually: top face gets a hole (1 face with inner loop), bottom stays (1 face),
        # 4 outer sides (4 faces), 3 new inner cut walls (the cut shares 2 edges with outer walls)
        # Let's just count total planar faces
        planar_faces = result.faces("%Plane").size()
        # Expected: 6 original - 0 removed + cut walls
        # The cut at top-right corner shares 2 walls with existing outer faces
        # So new walls = 2 inner walls + the cut modifies 2 outer faces
        # Total planar faces: bottom(1) + top-with-hole(1) + 4 outer sides + 2 inner cut walls = 8
        # But the 2 outer sides that are partially cut may split... let's check
        # Actually the cut is at the corner, so it shares exactly the corner edges
        # The right outer face (x=25) and top outer face (y=25) are NOT split because the cut
        # goes all the way to those faces — those faces remain intact but shorter
        # Hmm, let me reconsider: the cut removes a 10x10 chunk from the corner
        # Right face (x=25): originally y in [-25,25], after cut y in [-25,15] (the part y in [15,25] is removed)
        # Top face (y=25): originally x in [-25,25], after cut x in [-25,15]
        # So right face is split? No — the cut removes the corner, so the right face at x=25 
        # now only spans y from -25 to 15 (the top 10mm is gone)
        # Similarly top face at y=25 spans x from -25 to 15
        # New inner walls: x=15 (y from 15 to 25), y=15 (x from 15 to 25)
        # Total: bottom(1) + top-with-notch(1) + left(1) + front(1) + right-trimmed(1) + back-trimmed(1) + 2 inner = 8
        assert planar_faces == 8, f"Expected 8 planar faces, got {planar_faces}"
    
        # Verify the cut is at the correct corner by checking faces intersected by a vertical line
        # through the cut center (20, 20) — should intersect top and bottom faces only (not solid there)
        faces_through_cut = result.val().facesIntersectedByLine((20, 20, -1), (0, 0, 1))
        # The line goes through the cut, so it should hit the bottom face and the top face opening
        # Actually since the material is removed, the line through (20,20) hits:
        # - bottom face at z=0 (if the cut goes all the way through)
        # - top face boundary (the notch in the top face)
        # Let's just verify the line through the solid center hits faces
        faces_through_center = result.val().facesIntersectedByLine((0, 0, -1), (0, 0, 1))
        assert len(faces_through_center) >= 2, \
            f"Line through center should intersect at least 2 faces, got {len(faces_through_center)}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520976/gpt_generated.stl')
