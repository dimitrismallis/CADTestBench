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
        # Base rectangle (marginally extruded)
        base_length = 0.345    # X dimension
        base_width  = 0.0024   # Y dimension
        base_height = 0.00375  # Z dimension (marginal extrusion)
    
        # Rod dimensions (pointing upward in Z)
        rod_x      = 0.00375   # X dimension of rod
        rod_y      = 0.0075    # Y dimension of rod
        rod_height = 0.75      # Z dimension (height, pointing upward)
    
        # --- Step 1: Create the base plate (marginally extruded rectangle) ---
        # Centered at origin in XY, base sits on XY plane (Z from 0 to base_height)
        base = (
            cq.Workplane("XY")
            .box(base_length, base_width, base_height, centered=(True, True, False))
        )
    
        # --- Step 2: Create the rod at one corner of the base rectangle ---
        # The base plate spans:
        #   X: -base_length/2 to +base_length/2
        #   Y: -base_width/2  to +base_width/2
        #   Z: 0 to base_height
        #
        # Place rod at the (+X, +Y) corner of the base plate.
        # The rod's corner (min-X, min-Y) aligns with the base corner (max-X, max-Y).
        # So rod center in X: base_length/2 - rod_x/2
        #    rod center in Y: base_width/2  - rod_y/2
        # Rod sits on top of base (Z starts at base_height).
        #
        # Note: rod_y (0.0075) > base_width (0.0024), so rod extends beyond base in Y.
        # The rod's Y range: from (base_width/2 - rod_y) to base_width/2
        #   = (0.0012 - 0.0075) to 0.0012 = -0.0063 to 0.0012
    
        rod_cx = base_length / 2 - rod_x / 2
        rod_cy = base_width  / 2 - rod_y / 2
    
        rod = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(rod_cx, rod_cy, base_height))
            .box(rod_x, rod_y, rod_height, centered=(True, True, False))
        )
    
        # --- Step 3: Union base and rod ---
        result = base.union(rod)
    
        # --- Final object verification ---
        TOL = 1e-5
    
        # Check bounding box
        bb = result.val().BoundingBox()
    
        # X: base_length = 0.345 (base dominates in X since 0.345 >> 0.00375)
        # Rod X range: rod_cx - rod_x/2 to rod_cx + rod_x/2
        #            = (base_length/2 - rod_x/2) - rod_x/2 to (base_length/2 - rod_x/2) + rod_x/2
        #            = base_length/2 - rod_x to base_length/2
        # Base X range: -base_length/2 to base_length/2
        # Overall X: -base_length/2 to base_length/2 => xlen = base_length
        expected_xlen = base_length
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
    
        # Y: rod_y (0.0075) > base_width (0.0024), so rod dominates in Y
        # Base Y range: -base_width/2 to +base_width/2 = -0.0012 to 0.0012
        # Rod Y range: rod_cy - rod_y/2 to rod_cy + rod_y/2
        #            = (base_width/2 - rod_y/2) - rod_y/2 to (base_width/2 - rod_y/2) + rod_y/2
        #            = base_width/2 - rod_y to base_width/2
        #            = 0.0012 - 0.0075 to 0.0012 = -0.0063 to 0.0012
        # Overall Y min: min(-0.0012, -0.0063) = -0.0063
        # Overall Y max: max(0.0012, 0.0012) = 0.0012
        # Overall Y len: 0.0012 - (-0.0063) = 0.0075
        expected_ymin = base_width / 2 - rod_y
        expected_ymax = base_width / 2
        expected_ylen = rod_y  # rod dominates
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y width: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.ymin - expected_ymin) < TOL, \
            f"Y min: expected {expected_ymin}, got {bb.ymin}"
        assert abs(bb.ymax - expected_ymax) < TOL, \
            f"Y max: expected {expected_ymax}, got {bb.ymax}"
    
        # Z: base_height + rod_height = 0.00375 + 0.75 = 0.75375
        expected_zlen = base_height + rod_height
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z height: expected {expected_zlen}, got {bb.zlen}"
    
        # Z min should be 0
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
    
        # Z max should be base_height + rod_height
        assert abs(bb.zmax - expected_zlen) < TOL, \
            f"Z max: expected {expected_zlen}, got {bb.zmax}"
    
        # Volume check: base + rod (no overlap since rod sits on top of base)
        base_vol = base_length * base_width * base_height
        rod_vol  = rod_x * rod_y * rod_height
        expected_vol = base_vol + rod_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Check rod is taller than wide (pointing upward)
        assert rod_height > rod_x, "Rod height should be greater than rod X dimension"
        assert rod_height > rod_y, "Rod height should be greater than rod Y dimension"
    
        # Check explicit rod height value
        assert abs(rod_height - 0.75) < TOL, \
            f"Rod height: expected 0.75, got {rod_height}"
    
        # Check base dimensions
        assert abs(base_length - 0.345) < TOL, \
            f"Base length: expected 0.345, got {base_length}"
        assert abs(base_width - 0.0024) < TOL, \
            f"Base width: expected 0.0024, got {base_width}"
    
        # Verify the model has exactly 1 solid after union
        assert result.solids().size() == 1, \
            f"Expected 1 solid after union, got {result.solids().size()}"
    
        print(f"Base volume:  {base_vol:.8f}")
        print(f"Rod volume:   {rod_vol:.8f}")
        print(f"Total volume: {actual_vol:.8f}")
        print(f"Bounding box: X={bb.xlen:.6f}, Y={bb.ylen:.6f}, Z={bb.zlen:.6f}")
        print(f"Y range: [{bb.ymin:.6f}, {bb.ymax:.6f}]")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00019066/gpt_generated.stl')
