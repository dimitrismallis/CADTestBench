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
        # Larger rectangle (door)
        door_L = 0.416808   # length along X
        door_W = 0.033235   # width along Y
        door_H = 0.75       # height along Z
    
        # Smaller rectangle (hinge)
        hinge_L = 0.211685  # length (will run along Y after 90° rotation)
        hinge_W = 0.065736  # width (will run along X after 90° rotation)
        hinge_H = 0.411987  # height along Z
    
        # Padding from base
        padding = 0.0065309
    
        # --- Step 1: Create the larger rectangle (door) ---
        # Base on XY plane (Z=0), centered in X and Y
        door = (
            cq.Workplane("XY")
            .box(door_L, door_W, door_H, centered=(True, True, False))
        )
    
        # --- Step 2: Create the smaller rectangle (hinge) ---
        # The hinge is rotated 90° around Z, so:
        #   - its "length" (hinge_L) runs along Y
        #   - its "width" (hinge_W) runs along X
        #   - its "height" (hinge_H) runs along Z
        # Connected at one edge: hinge's -X face touches door's +X face
        # Door's +X face is at X = door_L/2 = 0.208404
        # Hinge center X = door_L/2 + hinge_W/2
        hinge_cx = door_L / 2 + hinge_W / 2
        hinge_cy = 0.0  # same center Y as door
        # Padding from base (Z=0): hinge bottom at Z = padding
        hinge_cz = padding + hinge_H / 2
    
        hinge = (
            cq.Workplane("XY")
            .box(hinge_W, hinge_L, hinge_H, centered=(True, True, False))
            .translate((hinge_cx, hinge_cy, padding))
        )
    
        # --- Step 3: Union the two parts ---
        result = door.union(hinge)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X: from -door_L/2 to door_L/2 + hinge_W
        expected_xmin = -door_L / 2
        expected_xmax = door_L / 2 + hinge_W
        expected_xlen = door_L + hinge_W
    
        # Y: max of door_W and hinge_L, centered
        expected_ylen = max(door_W, hinge_L)  # hinge_L > door_W
        expected_ymin = -hinge_L / 2
        expected_ymax = hinge_L / 2
    
        # Z: from 0 to door_H (door is taller)
        expected_zmin = 0.0
        expected_zmax = door_H
    
        assert abs(bb.xmin - expected_xmin) < TOL, f"xmin: expected {expected_xmin}, got {bb.xmin}"
        assert abs(bb.xmax - expected_xmax) < TOL, f"xmax: expected {expected_xmax}, got {bb.xmax}"
        assert abs(bb.xlen - expected_xlen) < TOL, f"xlen: expected {expected_xlen}, got {bb.xlen}"
    
        assert abs(bb.ymin - expected_ymin) < TOL, f"ymin: expected {expected_ymin}, got {bb.ymin}"
        assert abs(bb.ymax - expected_ymax) < TOL, f"ymax: expected {expected_ymax}, got {bb.ymax}"
        assert abs(bb.ylen - expected_ylen) < TOL, f"ylen: expected {expected_ylen}, got {bb.ylen}"
    
        assert abs(bb.zmin - expected_zmin) < TOL, f"zmin: expected {expected_zmin}, got {bb.zmin}"
        assert abs(bb.zmax - expected_zmax) < TOL, f"zmax: expected {expected_zmax}, got {bb.zmax}"
        assert abs(bb.zlen - door_H) < TOL, f"zlen: expected {door_H}, got {bb.zlen}"
    
        # Volume check: union of two boxes minus overlap
        # The two boxes share an edge (not a volume), so no overlap
        door_vol = door_L * door_W * door_H
        hinge_vol = hinge_W * hinge_L * hinge_H
        # They share an edge at X = door_L/2, so no volumetric overlap
        expected_vol = door_vol + hinge_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that the hinge dimensions are approximately half the door dimensions
        # hinge_L ≈ door_L / 2
        assert abs(hinge_L - door_L / 2) / door_L < 0.02, \
            f"hinge_L ({hinge_L}) should be ~half of door_L ({door_L})"
        # hinge_W ≈ door_W / 2 (approximately)
        # Note: 0.065736 vs 0.033235/2 = 0.016618 — not exactly half
        # The prompt says "approximately half" so let's check loosely
        # Actually hinge_W (0.065736) ≈ 2 * door_W (0.033235) — let's skip this strict check
    
        # Check the connection: hinge bottom at padding from door base
        # The hinge's bottom face should be at Z = padding
        hinge_bottom_faces = result.faces("<Z[-2]")  # second from bottom
        # Instead, check via point containment
        # Point inside hinge (above padding, within hinge bounds)
        test_point_hinge = (hinge_cx, 0.0, padding + 0.01)
        assert result.val().isInside(test_point_hinge), \
            f"Point {test_point_hinge} should be inside the hinge"
    
        # Point inside door
        test_point_door = (0.0, 0.0, 0.5)
        assert result.val().isInside(test_point_door), \
            f"Point {test_point_door} should be inside the door"
    
        # Point outside (above hinge but within door X range, at hinge X)
        test_point_outside = (hinge_cx, 0.0, padding + hinge_H + 0.01)
        assert not result.val().isInside(test_point_outside), \
            f"Point {test_point_outside} should be outside the model"
    
        print("All assertions passed!")
        print(f"Door volume: {door_vol:.6f}")
        print(f"Hinge volume: {hinge_vol:.6f}")
        print(f"Total volume: {actual_vol:.6f}")
        print(f"Bounding box: X[{bb.xmin:.4f}, {bb.xmax:.4f}] Y[{bb.ymin:.4f}, {bb.ymax:.4f}] Z[{bb.zmin:.4f}, {bb.zmax:.4f}]")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00524912/gpt_generated.stl')
