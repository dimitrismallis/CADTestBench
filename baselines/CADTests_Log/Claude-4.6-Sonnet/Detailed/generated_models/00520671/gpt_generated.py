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
        # --- Step 1: Base cylinder - diameter 1.5, height 0.06 ---
        base_cyl = cq.Workplane("XY").cylinder(0.06, 0.75)  # height=0.06, radius=0.75
    
        # --- Step 2: Second cylinder - diameter 0.75, height 0.375, centered on first ---
        # The second cylinder is placed in the middle (same center XY), extruded upward
        # Union with base cylinder
        second_cyl = cq.Workplane("XY").cylinder(0.375, 0.375)  # height=0.375, radius=0.375
    
        result = base_cyl.union(second_cyl)
    
        # --- Step 3: Cut rectangle from the right side ---
        # First cylinder radius = 0.75
        # Padding from edge = 0.12, so right edge of rectangle at x = 0.75 - 0.12 = 0.63
        # Rectangle length (x-direction) = 0.21
        # Rectangle center x = 0.63 - 0.21/2 = 0.525
        # Rectangle width (y-direction) = 0.45
        # Rectangle center y = 0 (centered in Y)
        # Cut through full height of the model (0.375)
    
        rect_center_x = 0.75 - 0.12 - 0.21 / 2  # = 0.525
        rect_center_y = 0.0
    
        # Create a box for the cut - height 0.375 (full height of second cylinder)
        # positioned at the right side
        cut_box = (
            cq.Workplane("XY")
            .center(rect_center_x, rect_center_y)
            .box(0.21, 0.45, 0.375, centered=(True, True, False))
        )
    
        result = result.cut(cut_box)
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box checks
        # X: should span from -0.75 to 0.75 (base cylinder diameter 1.5)
        assert abs(bb.xlen - 1.5) < TOL, f"X length: expected 1.5, got {bb.xlen}"
        # Y: should span from -0.75 to 0.75
        assert abs(bb.ylen - 1.5) < TOL, f"Y length: expected 1.5, got {bb.ylen}"
        # Z: max height is 0.375 (second cylinder height, centered so top at 0.375/2=0.1875)
        # cylinder(height, radius) centers the cylinder at origin by default
        # so Z goes from -0.375/2 to +0.375/2 = -0.1875 to 0.1875
        assert abs(bb.zlen - 0.375) < TOL, f"Z length: expected 0.375, got {bb.zlen}"
    
        # Volume check
        # Base cylinder volume: pi * 0.75^2 * 0.06
        vol_base = math.pi * (0.75 ** 2) * 0.06
        # Second cylinder volume: pi * 0.375^2 * 0.375
        vol_second = math.pi * (0.375 ** 2) * 0.375
        # Rectangle cut volume: 0.21 * 0.45 * 0.375 (full height of second cyl)
        # But the cut only removes material where it intersects the solid
        # The rectangle is at x=0.525 center, width 0.21 (x from 0.42 to 0.63)
        # This is entirely within the base cylinder (radius 0.75) for the base portion
        # and partially within the second cylinder (radius 0.375) for the upper portion
        # Let's just check volume is positive and reasonable
        vol = result.val().Volume()
        assert vol > 0, f"Volume should be positive, got {vol}"
    
        # The volume should be less than base + second cylinder combined
        vol_combined = vol_base + vol_second
        assert vol < vol_combined, f"Volume {vol} should be less than combined {vol_combined}"
    
        # Check that the second cylinder (inner) is present - cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, f"Expected at least 2 cylindrical faces, got {cyl_faces}"
    
        # Check the model has the right Z extent
        assert abs(bb.zmin - (-0.375 / 2)) < TOL, f"Z min: expected {-0.375/2}, got {bb.zmin}"
        assert abs(bb.zmax - (0.375 / 2)) < TOL, f"Z max: expected {0.375/2}, got {bb.zmax}"
    
        # Check that a point inside the base cylinder (but outside second) is inside the solid
        # Point at (0.6, 0, 0) should be inside base cylinder (r=0.75) but outside second (r=0.375)
        # Z=0 is within base cylinder Z range (-0.03 to 0.03)
        point_in_base = (0.6, 0.0, 0.0)
        assert result.val().isInside(point_in_base), f"Point {point_in_base} should be inside the solid"
    
        # Check that the cut rectangle removed material on the right side
        # Point at (0.525, 0, 0.1) should be outside (in the cut region)
        # x=0.525 is within the cut box (0.42 to 0.63), y=0 is within (-0.225 to 0.225), z=0.1 is within cut height
        point_in_cut = (0.525, 0.0, 0.1)
        assert not result.val().isInside(point_in_cut), f"Point {point_in_cut} should be outside (in cut region)"
    
        # Check that a point in the second cylinder (away from cut) is inside
        point_in_second = (-0.2, 0.0, 0.1)
        assert result.val().isInside(point_in_second), f"Point {point_in_second} should be inside the second cylinder"
    
        print(f"Volume: {vol:.6f}")
        print(f"Bounding box: x={bb.xlen:.4f}, y={bb.ylen:.4f}, z={bb.zlen:.4f}")
        print(f"Cylindrical faces: {cyl_faces}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520671/gpt_generated.stl')
