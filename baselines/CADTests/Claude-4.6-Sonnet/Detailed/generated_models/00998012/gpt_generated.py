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
        base_length = 0.9375   # X
        base_width  = 1.5      # Y
        base_height = 0.375    # Z
    
        l_arm_short = 0.234375  # short arm length (X direction)
        l_height    = 0.328125  # extrusion height of L block
        # The long arm uses the full base length (0.9375) in X
        # The L is aligned to one corner of the base rectangle
    
        # --- Step 1: Base block centered at XY origin, Z from 0 to base_height ---
        base = cq.Workplane("XY").box(base_length, base_width, base_height,
                                       centered=(True, True, False))
        # base occupies X: [-0.46875, 0.46875], Y: [-0.75, 0.75], Z: [0, 0.375]
    
        # --- Step 2: L-shaped sketch on top of base block ---
        # The L is aligned to the corner at (-X, -Y) = (-0.46875, -0.75)
        # 
        # L-shape profile (in XY plane at Z = base_height):
        # The L consists of:
        #   - Long arm:  full length 0.9375 in X, thickness = (base_width - l_arm_short) in Y
        #                from x=-0.46875 to x=0.46875, y=-0.75 to y=(-0.75 + base_width - l_arm_short)
        #   - Short arm: length l_arm_short in X, full width 1.5 in Y
        #                from x=-0.46875 to x=(-0.46875 + l_arm_short), y=-0.75 to y=0.75
        #
        # Together they form an L shape anchored at the (-X, -Y) corner.
        #
        # Let's define the L polygon vertices (in local XY coords on the top face):
        # Corner at bottom-left of base = (-base_length/2, -base_width/2)
    
        x0 = -base_length / 2   # -0.46875
        x1 = x0 + l_arm_short   # -0.46875 + 0.234375 = -0.234375
        x2 = base_length / 2    #  0.46875
    
        y0 = -base_width / 2    # -0.75
        y1 = base_width / 2     #  0.75
        # The long arm's Y extent: from y0 to y0 + (base_width - l_arm_short)
        # But we need a thickness for the long arm. 
        # Re-reading: "one arm having a length of 0.234375 and height 0.328125"
        # "other arm using the length of the base rectangle (0.9375)"
        # I interpret: short arm width = 0.234375 (in X), long arm width = 0.9375 (in X = full base)
        # The L thickness (Y direction for long arm) is not specified - use l_arm_short as thickness
        # So long arm: full X (0.9375) × l_arm_short thick in Y
        # Short arm: l_arm_short wide in X × full Y (1.5)
    
        # L polygon vertices (CCW):
        # Start at bottom-left corner, go around the L shape
        # The L occupies the bottom strip (long arm) + left column (short arm)
    
        y_long_arm_top = y0 + l_arm_short  # -0.75 + 0.234375 = -0.515625
    
        # L vertices (CCW when viewed from +Z):
        # Bottom-left -> Bottom-right -> top of long arm right -> top of long arm left (= short arm right) 
        # -> top of short arm -> top-left -> back to bottom-left
    
        l_pts = [
            (x0, y0),           # bottom-left corner
            (x2, y0),           # bottom-right corner  
            (x2, y_long_arm_top),  # top-right of long arm
            (x1, y_long_arm_top),  # inner corner of L
            (x1, y1),           # top of short arm right side
            (x0, y1),           # top-left corner
        ]
    
        # Create the L-shaped extrusion on top of the base
        l_block = (
            cq.Workplane("XY")
            .workplane(offset=base_height)
            .moveTo(l_pts[0][0], l_pts[0][1])
            .lineTo(l_pts[1][0], l_pts[1][1])
            .lineTo(l_pts[2][0], l_pts[2][1])
            .lineTo(l_pts[3][0], l_pts[3][1])
            .lineTo(l_pts[4][0], l_pts[4][1])
            .lineTo(l_pts[5][0], l_pts[5][1])
            .close()
            .extrude(l_height)
        )
    
        # --- Step 3: Union base and L-block ---
        result = base.union(l_block)
    
        # --- Step 4: Translate vertically by half the base height ---
        # "centered by translating it vertically by half the height of the base block"
        translate_z = base_height / 2  # 0.1875
        result = result.translate((0, 0, translate_z))
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
    
        # After translation by 0.1875:
        # Base: Z from 0.1875 to 0.5625
        # L-block: Z from 0.5625 to 0.890625
        expected_zmin = 0.1875
        expected_zmax = base_height + l_height + translate_z  # 0.375 + 0.328125 + 0.1875 = 0.890625
        expected_xlen = base_length   # 0.9375
        expected_ylen = base_width    # 1.5
        expected_zlen = base_height + l_height  # 0.703125
    
        assert abs(bb.xlen - expected_xlen) < TOL, f"X length: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, f"Y length: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, f"Z length: expected {expected_zlen}, got {bb.zlen}"
        assert abs(bb.zmin - expected_zmin) < TOL, f"Z min: expected {expected_zmin}, got {bb.zmin}"
        assert abs(bb.zmax - expected_zmax) < TOL, f"Z max: expected {expected_zmax}, got {bb.zmax}"
    
        # Volume check:
        # Base volume: 0.9375 * 1.5 * 0.375
        base_vol = base_length * base_width * base_height
        # L-shape area: full rect - missing rectangle
        # Full rect area = base_length * base_width = 0.9375 * 1.5
        # Missing rect (top-right cutout): (base_length - l_arm_short) * (base_width - l_arm_short)
        missing_x = base_length - l_arm_short   # 0.703125
        missing_y = base_width - l_arm_short    # 1.265625
        l_area = base_length * base_width - missing_x * missing_y
        l_vol = l_area * l_height
        expected_vol = base_vol + l_vol
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check the L-block is present (non-planar top - L shape has 6 vertices in XY)
        # The overall solid should have more faces than a simple box (6)
        face_count = result.faces().size()
        assert face_count > 6, f"Face count should be > 6 for L+base shape, got {face_count}"
    
        # Check center of mass is shifted from XY center due to L-shape asymmetry
        com = cq.Shape.centerOfMass(result.val())
        # The L is in the -X, -Y quadrant relative to center, so COM should be shifted
        assert com.z > 0, f"Center of mass Z should be positive, got {com.z}"
    
        # Verify the structure spans the full base dimensions in X and Y
        assert abs(bb.xmax - bb.xmin - base_length) < TOL, \
            f"X span: expected {base_length}, got {bb.xmax - bb.xmin}"
        assert abs(bb.ymax - bb.ymin - base_width) < TOL, \
            f"Y span: expected {base_width}, got {bb.ymax - bb.ymin}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.6f}, Y={bb.ylen:.6f}, Z={bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Face count: {face_count}")
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00998012/gpt_generated.stl')
