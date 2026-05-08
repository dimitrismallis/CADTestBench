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
        sq_side = 1.5
        height = 0.09375
        tri_bottom = 1.125    # leg along bottom edge
        tri_right = 1.3125    # leg along right edge
    
        # --- Step 1: Create the base square box ---
        # Box centered at origin: X in [-0.75, 0.75], Y in [-0.75, 0.75], Z in [-height/2, height/2]
        base = cq.Workplane("XY").box(sq_side, sq_side, height)
    
        # --- Step 2: Define triangle vertices ---
        # Bottom-right corner of the square (in XY plane, centered box):
        #   x_max = 0.75, y_min = -0.75
        x_max = sq_side / 2       # 0.75
        y_min = -sq_side / 2      # -0.75
    
        # Triangle vertices:
        # A = bottom-right corner (right angle)
        # B = 1.125 units left along bottom edge from A
        # C = 1.3125 units up along right edge from A
        A = (x_max, y_min)
        B = (x_max - tri_bottom, y_min)   # (-0.375, -0.75)
        C = (x_max, y_min + tri_right)    # (0.75, 0.5625)
    
        # --- Step 3: Create the triangular cutter as an extruded prism ---
        # Use a workplane at the bottom of the box (z = -height/2)
        z_bottom = -height / 2
    
        triangle_cutter = (
            cq.Workplane(cq.Plane(origin=(0, 0, z_bottom), normal=(0, 0, 1)))
            .moveTo(A[0], A[1])
            .lineTo(B[0], B[1])
            .lineTo(C[0], C[1])
            .close()
            .extrude(height)
        )
    
        # --- Step 4: Subtract the triangle from the base box ---
        result = base.cut(triangle_cutter)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Check bounding box - should still be 1.5 x 1.5 x 0.09375
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - sq_side) < TOL, f"X length: expected {sq_side}, got {bb.xlen}"
        assert abs(bb.ylen - sq_side) < TOL, f"Y length: expected {sq_side}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # Check bounding box extents
        assert abs(bb.xmin - (-sq_side/2)) < TOL, f"xmin: expected {-sq_side/2}, got {bb.xmin}"
        assert abs(bb.xmax - (sq_side/2)) < TOL, f"xmax: expected {sq_side/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-sq_side/2)) < TOL, f"ymin: expected {-sq_side/2}, got {bb.ymin}"
        assert abs(bb.ymax - (sq_side/2)) < TOL, f"ymax: expected {sq_side/2}, got {bb.ymax}"
    
        # Volume check:
        # Square area = 1.5 * 1.5 = 2.25
        # Triangle area = 0.5 * 1.125 * 1.3125 = 0.73828125
        # Remaining area = 2.25 - 0.73828125 = 1.51171875
        # Volume = 1.51171875 * 0.09375
        sq_area = sq_side * sq_side
        tri_area = 0.5 * tri_bottom * tri_right
        remaining_area = sq_area - tri_area
        expected_vol = remaining_area * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that the bottom-right corner point is NOT inside the solid
        # (it was cut away)
        corner_point = (x_max - 0.01, y_min + 0.01, 0)  # just inside the cut triangle
        assert not result.val().isInside(corner_point), \
            f"Bottom-right corner area should be cut away but point {corner_point} is inside"
    
        # Check that a point in the top-left area IS inside the solid
        interior_point = (-0.5, 0.5, 0)
        assert result.val().isInside(interior_point), \
            f"Top-left area should be solid but point {interior_point} is not inside"
    
        # Check that a point in the remaining solid (bottom-left) IS inside
        bottom_left_point = (-0.6, -0.6, 0)
        assert result.val().isInside(bottom_left_point), \
            f"Bottom-left area should be solid but point {bottom_left_point} is not inside"
    
        # The cut creates a diagonal face (the hypotenuse of the triangle)
        # Total faces: 6 original box faces - 1 bottom-right corner area + 1 diagonal face
        # Actually: top, bottom (now L-shaped), 4 sides but right side is split, bottom edge split
        # The shape should have more than 6 faces due to the triangular cut
        face_count = result.faces().size()
        assert face_count >= 7, f"Expected at least 7 faces after triangular cut, got {face_count}"
    
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.6f}")
        print(f"Face count: {face_count}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00673788/gpt_generated.stl')
