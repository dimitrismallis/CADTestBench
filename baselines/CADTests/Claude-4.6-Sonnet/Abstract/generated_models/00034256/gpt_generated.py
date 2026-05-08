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
        outer_w = 40.0      # outer width of U
        outer_h = 30.0      # height of U arms + bottom
        wall_t  = 8.0       # wall/bottom thickness
        inner_w = outer_w - 2 * wall_t   # 24mm inner width
        inner_h = outer_h - wall_t       # 22mm inner height (open at top)
    
        cap_w   = 50.0      # closing rectangle width (wider than U)
        cap_h   = 8.0       # closing rectangle height
    
        depth   = 20.0      # extrusion depth (along Z)
    
        # --- Step 1: Define profile points ---
        # Profile is drawn in the XY plane.
        # X = width direction, Y = height direction, Z = extrusion direction.
        # Origin at bottom-center of the U.
    
        ow2 = outer_w / 2
        iw2 = inner_w / 2
        cw2 = cap_w / 2
    
        # Outer profile (U body + cap), counter-clockwise
        outer_pts = [
            (-ow2, 0),
            ( ow2, 0),
            ( ow2, outer_h),
            ( cw2, outer_h),
            ( cw2, outer_h + cap_h),
            (-cw2, outer_h + cap_h),
            (-cw2, outer_h),
            (-ow2, outer_h),
        ]
    
        # Inner void (open-top inner rectangle of the U), subtracted
        inner_pts = [
            (-iw2, wall_t),
            ( iw2, wall_t),
            ( iw2, outer_h),
            (-iw2, outer_h),
        ]
    
        # --- Step 2: Create the profile using CadQuery Sketch ---
        sketch = (
            cq.Sketch()
            .polygon(outer_pts, mode="a")
            .polygon(inner_pts, mode="s")
        )
    
        # --- Step 3: Extrude the sketch along Z ---
        result = (
            cq.Workplane("XY")
            .placeSketch(sketch)
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks:
        # XY plane sketch: X = width (cap_w=50), Y = profile height (outer_h+cap_h=38)
        # Extrusion along Z: Z = depth = 20
        expected_x = cap_w            # 50mm wide (cap is widest)
        expected_y = outer_h + cap_h  # 38mm tall (profile height in Y)
        expected_z = depth            # 20mm deep (extrusion along Z)
    
        assert abs(bb.xlen - expected_x) < TOL, f"X width: expected {expected_x}, got {bb.xlen}"
        assert abs(bb.ylen - expected_y) < TOL, f"Y height: expected {expected_y}, got {bb.ylen}"
        assert abs(bb.zlen - expected_z) < TOL, f"Z depth: expected {expected_z}, got {bb.zlen}"
    
        # Volume check:
        # Outer U area = outer_w * outer_h = 40 * 30 = 1200
        # Inner void area = inner_w * inner_h = 24 * 22 = 528
        # Cap area = cap_w * cap_h = 50 * 8 = 400
        # Total 2D area = 1200 - 528 + 400 = 1072
        # Volume = area * depth = 1072 * 20 = 21440
        u_area = outer_w * outer_h - inner_w * inner_h + cap_w * cap_h
        expected_vol = u_area * depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Check there is exactly 1 solid
        assert result.solids().size() == 1, f"Expected 1 solid, got {result.solids().size()}"
    
        # Check the bracket has a hollow U interior (inner void)
        # Sketch is in XY plane, extrusion along Z.
        # inner void center in XY: (0, wall_t + inner_h/2) = (0, 8+11) = (0, 19)
        # Z midpoint of extrusion: depth/2 = 10
        inner_void_point = (0.0, wall_t + inner_h / 2, depth / 2)
        assert not result.val().isInside(inner_void_point), \
            f"Inner void point {inner_void_point} should be outside the solid"
    
        # A point inside the bottom wall should be inside the solid
        # bottom wall center in XY: (0, wall_t/2) = (0, 4)
        bottom_wall_point = (0.0, wall_t / 2, depth / 2)
        assert result.val().isInside(bottom_wall_point), \
            f"Bottom wall point {bottom_wall_point} should be inside the solid"
    
        # A point inside the cap should be inside the solid
        # cap center in XY: (0, outer_h + cap_h/2) = (0, 34)
        cap_point = (0.0, outer_h + cap_h / 2, depth / 2)
        assert result.val().isInside(cap_point), \
            f"Cap point {cap_point} should be inside the solid"
    
        # A point inside the left arm should be inside the solid
        # left arm center in XY: (-ow2 + wall_t/2, wall_t + inner_h/2) = (-16, 19)
        left_arm_point = (-ow2 + wall_t / 2, wall_t + inner_h / 2, depth / 2)
        assert result.val().isInside(left_arm_point), \
            f"Left arm point {left_arm_point} should be inside the solid"
    
        # Check symmetry: center of mass should be at x=0 (symmetric about YZ plane)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X should be 0 (symmetric), got {com.x}"
    
        # Check planar faces count
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 8, f"Expected at least 8 planar faces, got {planar_faces}"
    
        print(f"✓ Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm")
        print(f"✓ Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f})")
        print(f"✓ Planar faces: {planar_faces}")
        print(f"✓ Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00034256/gpt_generated.stl')
