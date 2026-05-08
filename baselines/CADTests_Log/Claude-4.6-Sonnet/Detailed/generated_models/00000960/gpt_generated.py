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
        L1, W1, H1 = 0.75, 0.75, 0.00195          # first rectangle (box)
        L2, W2     = 0.281257, 0.0625              # second rectangle length & width
        H2         = H1 / 2                        # height of second rect = half of first
        # H2 = 0.000975
    
        # --- Step 1: First rectangle box, centered at origin ---
        # Spans x: [-0.375, 0.375], y: [-0.375, 0.375], z: [-0.000975, 0.000975]
        first_box = cq.Workplane("XY").box(L1, W1, H1)
    
        # --- Step 2: Second rectangle box ---
        # Connects to right edge of first box (x = 0.375), starting halfway up (z = 0)
        # Center of second box:
        #   x_center = 0.375 + L2/2
        #   y_center = 0 (centered in Y)
        #   z_center = 0 + H2/2  (bottom at z=0, top at z=H2)
        x2_center = L1 / 2 + L2 / 2
        y2_center = 0.0
        z2_center = H2 / 2   # = H1/4
    
        second_box = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(x2_center, y2_center, z2_center))
            .box(L2, W2, H2)
        )
    
        # --- Step 3: Union the two boxes ---
        result = first_box.union(second_box)
    
        # --- Final object verification ---
        TOL = 1e-5
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box checks
        # X: from -0.375 to 0.375 + 0.281257 = 0.656257
        expected_xmin = -L1 / 2
        expected_xmax =  L1 / 2 + L2
        expected_xlen =  L1 + L2   # 0.75 + 0.281257 = 1.031257
    
        # Y: from -0.375 to 0.375 (first box dominates)
        expected_ymin = -W1 / 2
        expected_ymax =  W1 / 2
        expected_ylen =  W1        # 0.75
    
        # Z: from -H1/2 to H1/2 (first box), second box from 0 to H2=H1/2
        expected_zmin = -H1 / 2   # -0.000975
        expected_zmax =  H1 / 2   #  0.000975
        expected_zlen =  H1       #  0.00195
    
        assert abs(bb.xmin - expected_xmin) < TOL, f"xmin: expected {expected_xmin}, got {bb.xmin}"
        assert abs(bb.xmax - expected_xmax) < TOL, f"xmax: expected {expected_xmax}, got {bb.xmax}"
        assert abs(bb.xlen - expected_xlen) < TOL, f"xlen: expected {expected_xlen}, got {bb.xlen}"
    
        assert abs(bb.ymin - expected_ymin) < TOL, f"ymin: expected {expected_ymin}, got {bb.ymin}"
        assert abs(bb.ymax - expected_ymax) < TOL, f"ymax: expected {expected_ymax}, got {bb.ymax}"
        assert abs(bb.ylen - expected_ylen) < TOL, f"ylen: expected {expected_ylen}, got {bb.ylen}"
    
        assert abs(bb.zmin - expected_zmin) < TOL, f"zmin: expected {expected_zmin}, got {bb.zmin}"
        assert abs(bb.zmax - expected_zmax) < TOL, f"zmax: expected {expected_zmax}, got {bb.zmax}"
        assert abs(bb.zlen - expected_zlen) < TOL, f"zlen: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check: first box + second box (no overlap since second starts at z=0, first goes to z=H1/2)
        # Actually the second box occupies z=[0, H2] and x=[0.375, 0.375+L2]
        # The first box occupies x=[-0.375, 0.375], so no X overlap with second box
        vol_first  = L1 * W1 * H1
        vol_second = L2 * W2 * H2
        expected_vol = vol_first + vol_second
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Check that the second box is present by probing a point inside it
        # A point inside second box: x=0.4, y=0, z=H2/2=0.0004875
        probe_inside_second = (L1/2 + L2/2, 0.0, H2/2)
        assert result.val().isInside(probe_inside_second, tolerance=1e-6), \
            f"Point {probe_inside_second} should be inside the second box"
    
        # Check that a point below the second box (in the gap) is NOT inside the solid
        # Below second box at its x-range: x=0.4, y=0, z=-H1/4 (below z=0, in first box region)
        # Actually first box extends there, so let's check outside entirely
        probe_outside = (L1/2 + L2/2, 0.0, -H1/4)
        assert not result.val().isInside(probe_outside, tolerance=1e-6), \
            f"Point {probe_outside} should NOT be inside the solid (below second box, outside first box x-range)"
    
        # Check that a point inside the first box is inside
        probe_inside_first = (0.0, 0.0, 0.0)
        assert result.val().isInside(probe_inside_first, tolerance=1e-6), \
            f"Point {probe_inside_first} should be inside the first box"
    
        print("All assertions passed!")
        print(f"  Bounding box: x=[{bb.xmin:.6f}, {bb.xmax:.6f}], y=[{bb.ymin:.6f}, {bb.ymax:.6f}], z=[{bb.zmin:.6f}, {bb.zmax:.6f}]")
        print(f"  Volume: {actual_vol:.8f} (expected {expected_vol:.8f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00000960/gpt_generated.stl')
