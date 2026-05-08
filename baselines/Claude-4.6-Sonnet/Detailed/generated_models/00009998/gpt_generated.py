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
        rect_length = 0.333333   # X direction
        rect_width  = 0.066667   # Y direction
        rect_height = 0.083333   # Z direction
        cyl_radius  = 0.022222
        cyl_height  = 0.666667
    
        # --- Step 1: Create the base extruded rectangle (box) ---
        # Centered at origin in XY, so it spans:
        # X: -0.166667 to +0.166667
        # Y: -0.033333 to +0.033333
        # Z:  0        to  0.083333  (centered=False in Z)
        base = (
            cq.Workplane("XY")
            .box(rect_length, rect_width, rect_height, centered=(True, True, False))
        )
    
        # --- Step 2: Create the cylinder on one side (near +X edge), protruding from top ---
        # Place cylinder center at x = rect_length/2 - cyl_radius (just inside the +X edge)
        # y = 0 (center of width)
        # The cylinder base sits on top of the rectangle (z = rect_height)
        # and extends upward by cyl_height
        cyl_x = rect_length / 2 - cyl_radius   # 0.166667 - 0.022222 = 0.144444
        cyl_y = 0.0
        cyl_z_base = rect_height               # 0.083333
    
        cylinder = (
            cq.Workplane("XY")
            .workplane(offset=cyl_z_base)
            .center(cyl_x, cyl_y)
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # --- Step 3: Union the base rectangle and cylinder ---
        result = base.union(cylinder)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: rectangle dominates, from -rect_length/2 to +rect_length/2
        expected_xlen = rect_length
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected ~{expected_xlen:.6f}, got {bb.xlen:.6f}"
    
        # Y extent: rectangle dominates (wider than cylinder diameter)
        expected_ylen = rect_width
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected ~{expected_ylen:.6f}, got {bb.ylen:.6f}"
    
        # Z extent: rect_height + cyl_height
        expected_zlen = rect_height + cyl_height
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected ~{expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Z min should be 0 (base of rectangle)
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin:.6f}"
    
        # Z max should be rect_height + cyl_height
        expected_zmax = rect_height + cyl_height
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"Z max: expected ~{expected_zmax:.6f}, got {bb.zmax:.6f}"
    
        # Volume check: box volume + cylinder volume
        box_vol = rect_length * rect_width * rect_height
        cyl_vol = math.pi * cyl_radius**2 * cyl_height
        expected_vol = box_vol + cyl_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces exist (the cylinder contributes at least one)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check the cylinder is inside the bounding box on the +X side
        # The cylinder center at x=cyl_x should be inside the solid
        cyl_top_center = (cyl_x, cyl_y, rect_height + cyl_height / 2)
        assert result.val().isInside(cyl_top_center), \
            f"Cylinder mid-point {cyl_top_center} should be inside the solid"
    
        # Check the base rectangle region is solid
        rect_mid = (0.0, 0.0, rect_height / 2)
        assert result.val().isInside(rect_mid), \
            f"Rectangle center {rect_mid} should be inside the solid"
    
        # Check length is ~5x width
        ratio = rect_length / rect_width
        assert abs(ratio - 5.0) < 0.1, \
            f"Length/width ratio: expected ~5.0, got {ratio:.4f}"
    
        # Check cylinder radius is ~1/3 of rect_width
        ratio_r = cyl_radius / rect_width
        assert abs(ratio_r - 1/3) < 0.01, \
            f"Cylinder radius / rect_width: expected ~0.333, got {ratio_r:.4f}"
    
        print("All assertions passed!")
        print(f"  Bounding box: X={bb.xlen:.6f}, Y={bb.ylen:.6f}, Z={bb.zlen:.6f}")
        print(f"  Volume: {actual_vol:.6f} (expected ~{expected_vol:.6f})")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00009998/gpt_generated.stl')
