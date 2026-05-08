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
        outer_radius    = 8.0    # mm, same for both halves
        small_hole_r    = 4.0    # mm, smaller hole radius (diameter = 8mm)
        large_hole_r    = 6.0    # mm, larger hole radius (diameter = 12mm)
        half_length     = 20.0   # mm, length of each half
        # Ratio check: small_hole_d / large_hole_d = 8/12 = 2/3 ✓
    
        # --- Step 1: First half — annular cross-section with small hole, extruded 20mm ---
        # Sketch on XY plane: outer circle minus inner (small) circle
        result = (
            cq.Workplane("XY")
            .circle(outer_radius)          # outer profile
            .circle(small_hole_r)          # inner hole (creates a pending wire that cuts)
            .extrude(half_length)          # extrude 20mm along +Z
        )
    
        # --- Step 2: Second half — annular cross-section with large hole, extruded 20mm ---
        # Move to the top face of the first half and sketch the second annular section
        result = (
            result
            .faces(">Z")                   # select top face of first half
            .workplane()                   # set workplane there
            .circle(outer_radius)          # outer profile (same outer diameter)
            .circle(large_hole_r)          # inner hole (larger, diameter = 12mm)
            .extrude(half_length)          # extrude another 20mm along +Z
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
        total_length = 2 * half_length  # 40mm
        outer_diameter = 2 * outer_radius  # 16mm
    
        assert abs(bb.zlen - total_length) < TOL, \
            f"Total Z length: expected {total_length}, got {bb.zlen}"
        assert abs(bb.xlen - outer_diameter) < TOL, \
            f"X diameter: expected {outer_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - outer_diameter) < TOL, \
            f"Y diameter: expected {outer_diameter}, got {bb.ylen}"
    
        # 2. Z extents
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - total_length) < TOL, \
            f"Z max: expected {total_length}, got {bb.zmax}"
    
        # 3. Volume check
        # First half: annulus with outer_r=8, inner_r=4, length=20
        vol_half1 = math.pi * (outer_radius**2 - small_hole_r**2) * half_length
        # Second half: annulus with outer_r=8, inner_r=6, length=20
        vol_half2 = math.pi * (outer_radius**2 - large_hole_r**2) * half_length
        expected_vol = vol_half1 + vol_half2
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 4. Cylindrical faces:
        # The two halves share the same outer radius, so the outer cylindrical surfaces
        # merge into a single face. We expect 3 cylindrical faces:
        #   - 1 merged outer surface (full 40mm length)
        #   - 1 inner surface of first half (small hole, r=4)
        #   - 1 inner surface of second half (large hole, r=6)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 3, \
            f"Cylindrical faces: expected 3, got {cyl_faces}"
    
        # 5. Planar faces:
        # - bottom face (z=0, annulus with small hole)
        # - top face (z=40, annulus with large hole)
        # - interface annular ring at z=20 (the step between small and large hole)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 3, \
            f"Planar faces: expected 3, got {planar_faces}"
    
        # 6. Check that the small hole is present at z=10 (midpoint of first half)
        # A point at the center of the small hole should be OUTSIDE the solid
        small_hole_test_pt = (0, 0, 10)  # center of pipe at mid-height of first half
        assert not result.val().isInside(small_hole_test_pt), \
            f"Point {small_hole_test_pt} should be outside (inside small hole), but isInside returned True"
    
        # 7. Check that the large hole is present at z=30 (midpoint of second half)
        large_hole_test_pt = (0, 0, 30)  # center of pipe at mid-height of second half
        assert not result.val().isInside(large_hole_test_pt), \
            f"Point {large_hole_test_pt} should be outside (inside large hole), but isInside returned True"
    
        # 8. Check that the pipe wall is solid at z=10 (between small hole and outer wall)
        wall_test_pt_half1 = (6, 0, 10)  # inside the wall of first half (r=6, between 4 and 8)
        assert result.val().isInside(wall_test_pt_half1), \
            f"Point {wall_test_pt_half1} should be inside the pipe wall (first half), but isInside returned False"
    
        # 9. Check that the pipe wall is solid at z=30 (between large hole and outer wall)
        wall_test_pt_half2 = (7, 0, 30)  # inside the wall of second half (r=7, between 6 and 8)
        assert result.val().isInside(wall_test_pt_half2), \
            f"Point {wall_test_pt_half2} should be inside the pipe wall (second half), but isInside returned False"
    
        # 10. Check that r=5 at z=30 is OUTSIDE (inside the large hole, r=6)
        inside_large_hole_pt = (5, 0, 30)  # r=5, inside large hole (r=6) at second half
        assert not result.val().isInside(inside_large_hole_pt), \
            f"Point {inside_large_hole_pt} should be outside (inside large hole), but isInside returned True"
    
        # 11. Check that r=5 at z=10 IS inside the solid (wall of first half, since small hole r=4)
        inside_wall_half1_pt = (5, 0, 10)  # r=5, inside wall of first half (hole r=4, outer r=8)
        assert result.val().isInside(inside_wall_half1_pt), \
            f"Point {inside_wall_half1_pt} should be inside the pipe wall (first half), but isInside returned False"
    
        # 12. Single solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # 13. Verify hole diameter ratio: small_hole_d / large_hole_d = 2/3
        ratio = (2 * small_hole_r) / (2 * large_hole_r)
        assert abs(ratio - 2/3) < 0.01, \
            f"Hole diameter ratio: expected 2/3 (~0.667), got {ratio:.4f}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00039681/gpt_generated.stl')
