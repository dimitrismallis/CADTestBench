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
        H = 120.0          # height of the outer rectangle
        W = 2 * H          # width = 240.0 (twice the height)
        D = H / 4          # depth = 30.0 (extrusion depth)
    
        hole_w = 5 * W / 12    # hole width = 100.0
        hole_h = 7 * H / 10    # hole height = 84.0
        fillet_r = 6.0         # rounded corner radius
    
        # --- Step 1: Compute hole positions ---
        # Total width used by two holes: 2 * hole_w = 200.0
        # Remaining horizontal space: W - 2*hole_w = 240 - 200 = 40.0
        # Split into 3 equal gaps (left wall, middle wall, right wall): 40/3 ≈ 13.33
        gap = (W - 2 * hole_w) / 3.0  # ~13.333
    
        # Center of left hole: -W/2 + gap + hole_w/2
        left_cx = -W / 2 + gap + hole_w / 2
        right_cx = W / 2 - gap - hole_w / 2
    
        # Holes are vertically centered: cy = 0
        hole_cy = 0.0
    
        # --- Step 2: Build the sketch using Sketch API ---
        # Outer rectangle with two rounded-corner rectangular holes
        sketch = (
            cq.Sketch()
            .rect(W, H)                                          # outer rectangle
            .push([(left_cx, hole_cy)])
            .rect(hole_w, hole_h, mode="s")                      # left hole (subtract)
            .reset()
            .push([(right_cx, hole_cy)])
            .rect(hole_w, hole_h, mode="s")                      # right hole (subtract)
            .reset()
        )
    
        # --- Step 3: Add rounded corners to the holes ---
        sketch = sketch.vertices().fillet(fillet_r)
    
        # --- Step 4: Extrude the sketch ---
        result = cq.Workplane("XY").placeSketch(sketch).extrude(D)
    
        # --- Final object verification ---
        TOL = 0.5  # tolerance for floating point comparisons
    
        # Check bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - W) < TOL, f"X length: expected {W}, got {bb.xlen}"
        assert abs(bb.ylen - H) < TOL, f"Y length: expected {H}, got {bb.ylen}"
        assert abs(bb.zlen - D) < TOL, f"Z length: expected {D}, got {bb.zlen}"
    
        # Check volume: outer box minus two holes (with filleted corners)
        outer_vol = W * H * D
        # hole area = rect area - 4 corner squares + 4 quarter circles
        hole_area_corrected = hole_w * hole_h - 4 * fillet_r**2 + math.pi * fillet_r**2
        expected_vol = outer_vol - 2 * hole_area_corrected * D
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Check symmetry: center of mass should be at x=0, y=0
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z - D / 2) < TOL, f"Center of mass Z: expected {D/2}, got {com.z}"
    
        # Check that holes exist: there should be cylindrical (rounded) faces from fillets
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 8, f"Expected at least 8 cylindrical faces (hole corners), got {cyl_faces}"
    
        # Check that points inside holes are NOT inside the solid
        # Left hole center (well inside the hole)
        left_hole_point = (left_cx, hole_cy, D / 2)
        assert not result.val().isInside(left_hole_point), \
            f"Left hole center should be outside solid, but isInside returned True"
    
        # Right hole center (well inside the hole)
        right_hole_point = (right_cx, hole_cy, D / 2)
        assert not result.val().isInside(right_hole_point), \
            f"Right hole center should be outside solid, but isInside returned True"
    
        # Check that a point in the middle wall IS inside the solid
        # Middle wall is between the two holes, centered at x=0
        mid_wall_point = (0.0, 0.0, D / 2)
        assert result.val().isInside(mid_wall_point), \
            f"Middle wall center should be inside solid, but isInside returned False"
    
        # Check that outer corner regions are inside the solid
        # Use points well away from edges/faces (at least 10mm from any boundary)
        # Top-left corner region of the block (solid material, not in a hole)
        # Left edge of left hole is at: left_cx - hole_w/2 = -W/2 + gap = -120 + 13.33 = -106.67
        # So the left wall region is between x=-120 and x=-106.67
        # A safe point in the left wall: x = -W/2 + gap/2 = -120 + 6.67 = -113.33
        left_wall_x = -W / 2 + gap / 2
        left_wall_point = (left_wall_x, 0.0, D / 2)
        assert result.val().isInside(left_wall_point), \
            f"Left wall region should be inside solid at ({left_wall_x:.2f}, 0, {D/2}), but isInside returned False"
    
        # Right wall region
        right_wall_x = W / 2 - gap / 2
        right_wall_point = (right_wall_x, 0.0, D / 2)
        assert result.val().isInside(right_wall_point), \
            f"Right wall region should be inside solid at ({right_wall_x:.2f}, 0, {D/2}), but isInside returned False"
    
        # Top wall region (above the holes): y > hole_h/2
        # Top of hole is at hole_h/2 = 42, top of block is at H/2 = 60
        # Safe point: y = (hole_h/2 + H/2) / 2 = (42 + 60) / 2 = 51
        top_wall_y = (hole_h / 2 + H / 2) / 2
        top_wall_point = (0.0, top_wall_y, D / 2)
        assert result.val().isInside(top_wall_point), \
            f"Top wall region should be inside solid at (0, {top_wall_y:.2f}, {D/2}), but isInside returned False"
    
        print(f"All assertions passed!")
        print(f"Dimensions: W={W}, H={H}, D={D}")
        print(f"Hole size: {hole_w} x {hole_h}, fillet r={fillet_r}")
        print(f"Hole centers: left=({left_cx:.2f}, 0), right=({right_cx:.2f}, 0)")
        print(f"Volume: {actual_vol:.1f} (expected {expected_vol:.1f})")
        print(f"Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997878/gpt_generated.stl')
