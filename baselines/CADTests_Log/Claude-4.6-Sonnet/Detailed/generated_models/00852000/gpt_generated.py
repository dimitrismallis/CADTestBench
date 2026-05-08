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
        outer_size = 0.830095
        outer_height = 0.1703531
        inner_size = 0.676879
        inner_depth = 0.105467
        center_circle_dia = 0.327945
        center_circle_height = 0.105467
        corner_circle_dia = 0.25606
        corner_circle_height = 0.094448
    
        # Box centered at origin: Z from -outer_height/2 to +outer_height/2
        bottom_z = -outer_height / 2   # = -0.08517655
        top_z    =  outer_height / 2   # = +0.08517655
    
        # --- Step 1: Base square box ---
        base = cq.Workplane("XY").box(outer_size, outer_size, outer_height)
    
        # --- Step 2: Hollow cut — explicit cutter box placed at top, cutting downward ---
        # The cutter is a box of inner_size x inner_size x inner_depth
        # positioned so its TOP aligns with box top (top_z) and bottom at top_z - inner_depth
        # centered=True means it's centered at origin in XY, and at cutter_center_z in Z
        cutter_center_z = top_z - inner_depth / 2
        cutter = (
            cq.Workplane(cq.Plane(origin=(0, 0, cutter_center_z), normal=(0, 0, 1)))
            .box(inner_size, inner_size, inner_depth)
        )
        result = base.cut(cutter)
    
        # --- Step 3: Center circle extruded upward from the bottom of the box ---
        # Circle sits on the bottom face (Z = bottom_z) and extrudes upward to bottom_z + center_circle_height
        center_cyl = (
            cq.Workplane(cq.Plane(origin=(0, 0, bottom_z), normal=(0, 0, 1)))
            .circle(center_circle_dia / 2)
            .extrude(center_circle_height)
        )
        result = result.union(center_cyl)
    
        # --- Step 4: Four corner circles on top of the square ---
        # Each circle sits on the top face (Z = top_z) and extrudes upward by corner_circle_height
        corner_offset = outer_size / 2 - corner_circle_dia / 2
        corner_positions = [
            ( corner_offset,  corner_offset),
            (-corner_offset,  corner_offset),
            (-corner_offset, -corner_offset),
            ( corner_offset, -corner_offset),
        ]
        for cx, cy in corner_positions:
            corner_cyl = (
                cq.Workplane(cq.Plane(origin=(cx, cy, top_z), normal=(0, 0, 1)))
                .circle(corner_circle_dia / 2)
                .extrude(corner_circle_height)
            )
            result = result.union(corner_cyl)
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
    
        # X and Y: outer_size dominates
        assert abs(bb.xlen - outer_size) < TOL, \
            f"X bounding box: expected {outer_size}, got {bb.xlen}"
        assert abs(bb.ylen - outer_size) < TOL, \
            f"Y bounding box: expected {outer_size}, got {bb.ylen}"
    
        # Z: bottom at bottom_z, top at top_z + corner_circle_height
        expected_zmin = bottom_z
        expected_zmax = top_z + corner_circle_height
        expected_zlen = outer_height + corner_circle_height
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"Z min: expected {expected_zmin:.6f}, got {bb.zmin:.6f}"
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"Z max: expected {expected_zmax:.6f}, got {bb.zmax:.6f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z bounding box: expected {expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Volume calculation:
        # base box
        base_vol = outer_size * outer_size * outer_height
        # hollow cut (removed)
        inner_cut_vol = inner_size * inner_size * inner_depth
        # center cylinder: from bottom_z to bottom_z + center_circle_height
        #   cyl top = bottom_z + center_circle_height = -0.08517655 + 0.105467 = 0.02029045
        #   hollow bottom = top_z - inner_depth = 0.08517655 - 0.105467 = -0.02029045
        #   cyl top (0.02029045) > hollow bottom (-0.02029045): overlap exists!
        #   overlap region: from hollow_bottom (-0.02029045) to cyl_top (0.02029045)
        #   overlap height = 0.02029045 - (-0.02029045) = 0.04058090
        #   overlap volume = pi * r^2 * overlap_height (circle fits inside hollow)
        cyl_top = bottom_z + center_circle_height       # = 0.02029045
        hollow_bottom = top_z - inner_depth             # = -0.02029045
        center_r = center_circle_dia / 2               # = 0.163973
        if cyl_top > hollow_bottom:
            overlap_height = cyl_top - hollow_bottom
            overlap_vol = math.pi * center_r**2 * overlap_height
        else:
            overlap_vol = 0.0
        center_circle_vol_net = math.pi * center_r**2 * center_circle_height - overlap_vol
        # corner circles (all above box top, no overlap with hollow)
        corner_r = corner_circle_dia / 2
        corner_circle_vol = 4 * math.pi * corner_r**2 * corner_circle_height
    
        expected_vol = base_vol - inner_cut_vol + center_circle_vol_net + corner_circle_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces (at least 5: 1 center + 4 corners)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 5, \
            f"Expected at least 5 cylindrical faces, got {cyl_faces}"
    
        # Check hollow: point in hollow annular region should be outside solid
        # hollow_x > center_r so it's outside the center cylinder
        hollow_x = inner_size / 2 * 0.8   # 0.270752 > center_r 0.163973
        hollow_test_z = top_z - inner_depth / 2
        hollow_point = (hollow_x, 0.0, hollow_test_z)
        assert not result.val().isInside(hollow_point), \
            f"Point {hollow_point} should be in hollow (outside solid)"
    
        # Check bottom wall is solid
        bottom_point = (0.0, 0.0, bottom_z + 0.005)
        assert result.val().isInside(bottom_point), \
            f"Point {bottom_point} should be inside solid bottom wall"
    
        # Check center circle region is solid (below hollow bottom)
        center_test_z = bottom_z + center_circle_height * 0.3
        center_point = (0.0, 0.0, center_test_z)
        assert result.val().isInside(center_point), \
            f"Point {center_point} should be inside center circle"
    
        # Check corner circle is solid above box top
        corner_test_z = top_z + corner_circle_height / 2
        corner_point = (corner_offset, corner_offset, corner_test_z)
        assert result.val().isInside(corner_point), \
            f"Point {corner_point} should be inside corner circle"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"Z extents: {bb.zmin:.6f} to {bb.zmax:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00852000/gpt_generated.stl')
