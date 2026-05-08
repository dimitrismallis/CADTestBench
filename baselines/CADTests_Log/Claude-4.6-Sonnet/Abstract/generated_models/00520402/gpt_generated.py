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
        outer_r = 20.0      # outer radius of hollow cylinder
        inner_r = 15.0      # inner radius (hole)
        length  = 100.0     # total length along Z
        wall    = outer_r - inner_r  # 5 mm wall thickness
    
        # --- Step 1: Create the hollow cylinder (tube) ---
        # Outer cylinder minus inner cylinder = hollow tube
        hollow_cyl = (
            cq.Workplane("XY")
            .circle(outer_r)
            .extrude(length)
        )
        hollow_cyl = (
            hollow_cyl
            .faces(">Z").workplane()
            .circle(inner_r)
            .cutThruAll()
        )
    
        # --- Step 2: Create the semi-circular cutter ---
        # Cut a semi-circular notch in the MIDDLE of the cylinder (centered at Z = length/2).
        # The cutter is a half-cylinder: full cylinder of radius outer_r+1, clipped to -Y half,
        # with height = 2*outer_r (diameter) centered at mid_z.
    
        mid_z = length / 2.0  # 50 mm
        cutter_r = outer_r + 1.0  # slightly larger than outer radius for clean cut
        cut_height = 2 * outer_r  # height of the semi-circular notch = 40 mm
    
        # Full cylinder for the cutter, centered at mid_z
        # Spans from Z = mid_z - outer_r to Z = mid_z + outer_r
        cutter_bottom_z = mid_z - outer_r  # Z = 30
        cutter_full = (
            cq.Workplane("XY", origin=(0, 0, cutter_bottom_z))
            .circle(cutter_r)
            .extrude(cut_height)
        )
    
        # Box covering the -Y half to intersect with the cylinder.
        # Must fully cover the cutter in Z (Z=30 to Z=70) and X.
        # Box: X centered, Y from -(cutter_r+1) to 0, Z must cover cutter_bottom_z to cutter_bottom_z+cut_height
        # Use a large Z extent centered at mid_z to ensure full coverage.
        large_z = cut_height + 10  # 50 mm, more than enough
        clip_box_neg = (
            cq.Workplane("XY", origin=(0, -(cutter_r + 1), mid_z))
            .box(2 * (cutter_r + 1), cutter_r + 1, large_z,
                 centered=(True, False, True))
        )
    
        # Semi-circular cutter = full cylinder intersected with -Y half box
        semi_cutter = cutter_full.intersect(clip_box_neg)
    
        # --- Step 3: Cut the semi-circular shape from the hollow cylinder ---
        result = hollow_cyl.cut(semi_cutter)
    
        # --- Final object verification ---
        TOL = 0.5  # generous tolerance for complex geometry
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        # X: should span -outer_r to +outer_r = 40 mm total (full tube width preserved)
        assert abs(bb.xlen - 2 * outer_r) < TOL, \
            f"X extent: expected {2*outer_r}, got {bb.xlen}"
    
        # Y: The semi-circular cut removes the -Y half only at the MIDDLE section.
        # The top and bottom portions of the tube still have the full -Y wall.
        # So ymin = -outer_r (wall still present at top/bottom), ymax = +outer_r
        assert abs(bb.ymin - (-outer_r)) < TOL, \
            f"Y min: expected {-outer_r}, got {bb.ymin}"
        assert abs(bb.ymax - outer_r) < TOL, \
            f"Y max: expected {outer_r}, got {bb.ymax}"
        assert abs(bb.ylen - 2 * outer_r) < TOL, \
            f"Y extent: expected {2*outer_r}, got {bb.ylen}"
    
        # Z: should span 0 to length = 100 mm
        assert abs(bb.zlen - length) < TOL, \
            f"Z extent: expected {length}, got {bb.zlen}"
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - length) < TOL, \
            f"Z max: expected {length}, got {bb.zmax}"
    
        # Volume check:
        # Full hollow cylinder volume = pi*(outer_r^2 - inner_r^2)*length
        full_hollow_vol = math.pi * (outer_r**2 - inner_r**2) * length
        # Semi-circular cut volume = half annular cross-section * cut_height
        # half of pi*(outer_r^2 - inner_r^2) * cut_height
        semi_cut_vol = 0.5 * math.pi * (outer_r**2 - inner_r**2) * cut_height
        expected_vol = full_hollow_vol - semi_cut_vol
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Check cylindrical faces exist (outer and inner surfaces)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces, got {cyl_faces}"
    
        # Check the semi-circular cut is present at mid_z on the -Y side:
        # A point in the wall on the -Y side at mid_z should NOT be inside the solid
        test_point_cut = (0, -(outer_r - wall / 2), mid_z)
        assert not result.val().isInside(test_point_cut), \
            f"Point {test_point_cut} should be outside (in the cut region)"
    
        # A point in the wall on the +Y side at mid_z should be inside the solid
        test_point_wall = (0, outer_r - wall / 2, mid_z)
        assert result.val().isInside(test_point_wall), \
            f"Point {test_point_wall} should be inside the solid (wall on +Y side)"
    
        # A point inside the hollow bore should NOT be inside the solid
        test_point_bore = (0, 0, mid_z)
        assert not result.val().isInside(test_point_bore), \
            f"Point {test_point_bore} should be outside (inside the bore)"
    
        # A point in the -Y wall near the bottom (Z=5) should still be inside (cut is only at middle)
        test_point_bottom_wall = (0, -(outer_r - wall / 2), 5.0)
        assert result.val().isInside(test_point_bottom_wall), \
            f"Point {test_point_bottom_wall} should be inside (wall preserved at bottom)"
    
        # A point in the -Y wall near the top (Z=95) should still be inside
        test_point_top_wall = (0, -(outer_r - wall / 2), 95.0)
        assert result.val().isInside(test_point_top_wall), \
            f"Point {test_point_top_wall} should be inside (wall preserved at top)"
    
        print("All assertions passed!")
        print(f"  Bounding box: X={bb.xlen:.2f}, Y={bb.ylen:.2f}, Z={bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} (expected ~{expected_vol:.2f})")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520402/gpt_generated.stl')
