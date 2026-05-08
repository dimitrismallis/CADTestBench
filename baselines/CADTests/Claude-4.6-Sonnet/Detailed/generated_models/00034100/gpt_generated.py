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
        length = 0.47368   # X dimension
        width  = 0.31579   # Y dimension
        height = 0.75      # Z dimension
    
        hole_diameter = 0.196206
        hole_radius   = hole_diameter / 2.0  # 0.098103
    
        # Top of hole is 0.146132 below top surface
        top_surface_z = height / 2.0          # 0.375 (block centered at origin)
        hole_top_z    = top_surface_z - 0.146132  # 0.228868
    
        slit_width  = 0.007895
        slit_depth  = 0.196132   # from top surface downward
        slit_bottom_z = top_surface_z - slit_depth  # 0.375 - 0.196132 = 0.178868
    
        # --- Step 1: Create the rectangular block centered at origin ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Create the circular hole ---
        # The hole top is at hole_top_z = 0.228868
        # The hole goes downward through the entire block (to z = -0.375)
        # depth = hole_top_z - (-height/2) = 0.228868 + 0.375 = 0.603868
        hole_depth = hole_top_z + height / 2.0  # distance from hole_top_z to bottom of block
    
        result = (
            result
            .workplane(offset=hole_top_z)   # workplane at z = hole_top_z
            .circle(hole_radius)
            .cutBlind(-hole_depth)          # cut downward (negative = into solid going -Z)
        )
    
        # --- Step 3: Create the thin slit ---
        # Slit: width 0.007895 in X, extends from center (y=0) to shorter edge (y = width/2)
        # Slit depth: from top surface (z=0.375) down to z=0.178868
        # Slit height = slit_depth = 0.196132
        # Slit length in Y = from 0 to width/2 = 0.157895
        slit_length_y = width / 2.0          # 0.157895 (from center to shorter edge)
        slit_center_y = slit_length_y / 2.0  # 0.078948 (center of slit in Y)
        slit_center_z = top_surface_z - slit_depth / 2.0  # center of slit in Z
    
        slit_box = (
            cq.Workplane("XY")
            .box(slit_width, slit_length_y, slit_depth,
                 centered=(True, True, True))
            .translate((0, slit_center_y, slit_center_z))
        )
        result = result.cut(slit_box)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Check bounding box of the overall result
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Check volume: block - cylinder hole - slit (with overlap correction)
        block_vol = length * width * height
        # Cylinder hole: from hole_top_z down to -height/2
        cyl_vol = math.pi * hole_radius**2 * hole_depth
        # Slit volume
        slit_vol = slit_width * slit_length_y * slit_depth
    
        # Overlap between slit and cylinder in the z-range [slit_bottom_z, hole_top_z]
        overlap_z = hole_top_z - slit_bottom_z  # 0.05
        y_max_in_cyl = math.sqrt(hole_radius**2 - (slit_width/2)**2)
        overlap_y = min(slit_length_y, y_max_in_cyl)
        overlap_vol = slit_width * overlap_y * overlap_z
    
        expected_vol = block_vol - cyl_vol - slit_vol + overlap_vol
        actual_vol = result.val().Volume()
    
        # Allow 2% tolerance
        assert abs(actual_vol - expected_vol) / block_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that there is a cylindrical face (the hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        solid = result.val()
    
        # Check the hole exists: points inside the cylinder region should be outside the solid
        # Test at multiple depths within the hole
        hole_mid_z = (hole_top_z + (-height/2.0)) / 2.0  # midpoint of hole depth
        assert not solid.isInside((0.0, 0.0, hole_mid_z), tolerance=0.001), \
            f"Point at hole midpoint should be outside solid (inside hole)"
    
        # Test just below hole_top_z (hole should exist here)
        just_below_top = hole_top_z - 0.01
        assert not solid.isInside((0.0, 0.0, just_below_top), tolerance=0.001), \
            f"Point just below hole top should be outside solid (inside hole)"
    
        # Test near bottom of block inside hole
        near_bottom = -height/2.0 + 0.01
        assert not solid.isInside((0.0, 0.0, near_bottom), tolerance=0.001), \
            f"Point near bottom inside hole should be outside solid"
    
        # Check the slit exists: a point inside the slit region should be outside the solid
        slit_test_point = (0.0, slit_center_y, slit_center_z)
        assert not solid.isInside(slit_test_point, tolerance=0.0001), \
            f"Point {slit_test_point} should be outside solid (inside slit)"
    
        # Check that the block material exists at corners (away from hole and slit)
        corner_test1 = (length/2.0 - 0.05, width/2.0 - 0.05, 0.0)
        assert solid.isInside(corner_test1, tolerance=0.001), \
            f"Point {corner_test1} should be inside solid (corner material)"
    
        corner_test2 = (-(length/2.0 - 0.05), -(width/2.0 - 0.05), 0.0)
        assert solid.isInside(corner_test2, tolerance=0.001), \
            f"Point {corner_test2} should be inside solid (opposite corner material)"
    
        # Check top and bottom surface Z positions
        assert abs(bb.zmax - top_surface_z) < TOL, \
            f"Top surface Z: expected {top_surface_z}, got {bb.zmax}"
        assert abs(bb.zmin - (-top_surface_z)) < TOL, \
            f"Bottom surface Z: expected {-top_surface_z}, got {bb.zmin}"
    
        # Check that material exists above hole_top_z at center (the cap above the hole)
        above_hole = (0.0, 0.0, hole_top_z + 0.05)
        assert solid.isInside(above_hole, tolerance=0.001), \
            f"Point above hole top should be inside solid (cap material)"
    
        # Check that material does NOT exist just above hole_top_z at center inside hole radius
        # (the hole top is a flat annular face, so directly above hole_top_z at center is solid)
        # But just below hole_top_z at center should be empty
        assert not solid.isInside((0.0, 0.0, hole_top_z - 0.005), tolerance=0.0005), \
            f"Point just below hole_top_z at center should be outside solid (in hole)"
    
        print("All assertions passed!")
        print(f"Block volume:          {block_vol:.6f}")
        print(f"Cylinder hole volume:  {cyl_vol:.6f}")
        print(f"Slit volume:           {slit_vol:.6f}")
        print(f"Overlap volume:        {overlap_vol:.6f}")
        print(f"Expected solid volume: {expected_vol:.6f}")
        print(f"Actual solid volume:   {actual_vol:.6f}")
        print(f"Bounding box: {bb.xlen:.5f} x {bb.ylen:.5f} x {bb.zlen:.5f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00034100/gpt_generated.stl')
