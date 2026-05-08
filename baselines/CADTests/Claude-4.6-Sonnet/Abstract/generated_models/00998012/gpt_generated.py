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
        base_len   = 80.0   # X
        base_wid   = 50.0   # Y
        base_h     = 20.0   # Z
    
        # L-shape arms (within the same 80x50 footprint)
        # Vertical arm of L: left side, full height of footprint
        v_arm_w    = 30.0   # width in X
        v_arm_d    = 50.0   # depth in Y (full)
    
        # Horizontal arm of L: top portion, full width
        h_arm_w    = 80.0   # width in X (full)
        h_arm_d    = 20.0   # depth in Y
    
        l_height   = 30.0   # extrusion height of L block
    
        # --- Step 1: Base rectangular block ---
        # Centered at origin: X in [-40, 40], Y in [-25, 25], Z in [0, 20]
        base = cq.Workplane("XY").box(base_len, base_wid, base_h)
    
        # --- Step 2: Build L-shaped profile on top of base ---
        # Work on the top face of the base (Z = base_h/2 = 10, but box is centered so top is at Z=10)
        # The base box is centered at (0,0,0), so Z goes from -10 to +10.
        # We need to work on the top face at Z = +10.
    
        # The L-shape is defined in the XY plane of the top face.
        # Base box corners: X in [-40, 40], Y in [-25, 25]
        # Align L with top-left corner: (-40, 25) in world XY.
        #
        # Vertical arm: X in [-40, -10], Y in [-25, 25]  → 30 wide, 50 deep
        # Horizontal arm: X in [-40, 40], Y in [5, 25]   → 80 wide, 20 deep
        # Union of these two rectangles = L-shape
    
        # We'll use the Sketch API to create the L profile as union of two rects.
        # In the workplane on top face, coordinates are local (same as world XY since
        # the workplane origin projects to center of top face = (0, 0, 10)).
    
        # Vertical arm center in local coords: x = (-40 + -10)/2 = -25, y = 0
        # Horizontal arm center in local coords: x = 0, y = (5 + 25)/2 = 15
    
        l_sketch = (
            cq.Sketch()
            # Vertical arm: 30 wide, 50 deep, centered at (-25, 0)
            .push([((-25.0), 0.0)])
            .rect(v_arm_w, v_arm_d)
            # Horizontal arm: 80 wide, 20 deep, centered at (0, 15)
            .push([(0.0, 15.0)])
            .rect(h_arm_w, h_arm_d)
            # Clean up: merge overlapping regions into one face
            .clean()
        )
    
        # --- Step 3: Extrude L-shape upward from top of base ---
        result = (
            base
            .faces(">Z")
            .workplane()
            .placeSketch(l_sketch)
            .extrude(l_height)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box: X should span full base width [-40, 40] = 80
        assert abs(bb.xlen - base_len) < TOL, f"X length: expected {base_len}, got {bb.xlen}"
        # Y should span full base depth [-25, 25] = 50
        assert abs(bb.ylen - base_wid) < TOL, f"Y length: expected {base_wid}, got {bb.ylen}"
        # Z: base_h + l_height = 50 total (box centered so Z: -10 to 10 for base, then +30 for L)
        total_h = base_h + l_height
        assert abs(bb.zlen - total_h) < TOL, f"Z length: expected {total_h}, got {bb.zlen}"
    
        # Volume check:
        # Base volume: 80 * 50 * 20 = 80000
        base_vol = base_len * base_wid * base_h
        # L-shape volume: union of two arms minus overlap
        # Vertical arm: 30 * 50 * 30 = 45000
        # Horizontal arm: 80 * 20 * 30 = 48000
        # Overlap (intersection): 30 * 20 * 30 = 18000
        v_arm_vol  = v_arm_w * v_arm_d * l_height
        h_arm_vol  = h_arm_w * h_arm_d * l_height
        overlap    = v_arm_w * h_arm_d * l_height
        l_vol      = v_arm_vol + h_arm_vol - overlap
        expected_vol = base_vol + l_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # The object should be a single solid (fused)
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Check that the top of the L is at the correct Z
        top_z = bb.zmax
        expected_top_z = base_h / 2 + l_height  # box centered: top of base at +10, L adds 30 → 40
        assert abs(top_z - expected_top_z) < TOL, \
            f"Top Z: expected {expected_top_z}, got {top_z}"
    
        # Check bottom of object
        bot_z = bb.zmin
        expected_bot_z = -base_h / 2  # box centered: bottom at -10
        assert abs(bot_z - expected_bot_z) < TOL, \
            f"Bottom Z: expected {expected_bot_z}, got {bot_z}"
    
        # The L-shape does NOT cover the full footprint at the top level
        # Verify a point inside the L (vertical arm) is inside the solid
        pt_in_v_arm = (float(-25), float(0), float(35))  # inside vertical arm, mid-height of L
        assert result.val().isInside(pt_in_v_arm), \
            f"Point {pt_in_v_arm} should be inside the vertical arm of L"
    
        # Verify a point inside the L (horizontal arm) is inside the solid
        pt_in_h_arm = (float(20), float(15), float(35))  # inside horizontal arm, mid-height of L
        assert result.val().isInside(pt_in_h_arm), \
            f"Point {pt_in_h_arm} should be inside the horizontal arm of L"
    
        # Verify a point in the cutout region of the L is NOT inside the solid
        pt_cutout = (float(20), float(-10), float(35))  # in the missing part of L
        assert not result.val().isInside(pt_cutout), \
            f"Point {pt_cutout} should be OUTSIDE the L (in the cutout region)"
    
        # Verify a point inside the base (below L) is inside the solid
        pt_base = (float(30), float(-15), float(0))  # inside base, outside L footprint
        assert result.val().isInside(pt_base), \
            f"Point {pt_base} should be inside the base block"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00998012/gpt_generated.stl')
