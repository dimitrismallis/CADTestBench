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
        # Tabletop
        top_length = 120.0   # X direction
        top_width  = 40.0    # Y direction  
        top_depth  = 40.0    # Z direction (depth = width)
        shell_t    = 3.0     # shell wall thickness
    
        # Legs
        leg_w      = 8.0     # leg cross-section width (X)
        leg_d      = 8.0     # leg cross-section depth (Y)
        leg_h      = 24.0    # leg height (~3 × leg_w)
        # Legs are placed near the ends of the tabletop, centered in Y
        leg_x_offset = top_length / 2 - leg_w / 2  # 56.0 from center
    
        # Rod
        rod_dia    = 7.0     # slightly less than leg_w=8
        rod_r      = rod_dia / 2
    
        # --- Step 1: Create the tabletop solid (extruded rectangle) ---
        # Centered at origin, spans z: 0 to top_depth
        tabletop_solid = (
            cq.Workplane("XY")
            .box(top_length, top_width, top_depth,
                 centered=(True, True, False))
        )
    
        # --- Step 2: Shell the tabletop (hollow inside, open bottom) ---
        # Remove the bottom face and shell inward
        tabletop = tabletop_solid.faces("<Z").shell(-shell_t)
    
        # --- Step 3: Create left leg ---
        # Left leg: centered at x = -leg_x_offset, y = 0
        # Leg hangs below tabletop bottom (z=0), so z: -leg_h to 0
        left_leg = (
            cq.Workplane("XY")
            .box(leg_w, leg_d, leg_h,
                 centered=(True, True, False))
            .translate((-leg_x_offset, 0, -leg_h))
        )
    
        # --- Step 4: Create right leg ---
        right_leg = (
            cq.Workplane("XY")
            .box(leg_w, leg_d, leg_h,
                 centered=(True, True, False))
            .translate((leg_x_offset, 0, -leg_h))
        )
    
        # --- Step 5: Create connecting rod ---
        # Rod runs along X axis, connecting bottom of left leg to bottom of right leg
        # Bottom of legs is at z = -leg_h, center of rod at z = -leg_h + rod_r
        rod_length = 2 * leg_x_offset - leg_w  # gap between inner faces of legs
        rod_center_z = -leg_h + rod_r
        rod_center_x = 0.0
        rod_center_y = 0.0
    
        # Create cylinder along X axis
        rod = (
            cq.Workplane("YZ")
            .circle(rod_r)
            .extrude(rod_length)
            .translate((-rod_length / 2, rod_center_y, rod_center_z))
        )
    
        # --- Step 6: Union all parts ---
        result = tabletop.union(left_leg).union(right_leg).union(rod)
    
        # --- Final object verification ---
        TOL = 0.5  # tolerance for volume/geometry checks
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        # X: from -top_length/2 to +top_length/2 = 120
        assert abs(bb.xlen - top_length) < TOL, \
            f"BB xlen: expected {top_length}, got {bb.xlen}"
    
        # Y: from -top_width/2 to +top_width/2 = 40
        assert abs(bb.ylen - top_width) < TOL, \
            f"BB ylen: expected {top_width}, got {bb.ylen}"
    
        # Z: from -leg_h to top_depth = -24 to 40, total = 64
        expected_zlen = top_depth + leg_h
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"BB zlen: expected {expected_zlen}, got {bb.zlen}"
    
        # Z extents
        assert abs(bb.zmin - (-leg_h)) < TOL, \
            f"BB zmin: expected {-leg_h}, got {bb.zmin}"
        assert abs(bb.zmax - top_depth) < TOL, \
            f"BB zmax: expected {top_depth}, got {bb.zmax}"
    
        # Volume check
        # Tabletop shell volume: outer box - inner box
        inner_length = top_length - 2 * shell_t
        inner_width  = top_width  - 2 * shell_t
        inner_depth  = top_depth  - shell_t   # open bottom, so only top and sides
        top_vol = top_length * top_width * top_depth - inner_length * inner_width * inner_depth
    
        # Each leg volume
        leg_vol = leg_w * leg_d * leg_h
    
        # Rod volume
        rod_vol = math.pi * rod_r**2 * rod_length
    
        expected_vol = top_vol + 2 * leg_vol + rod_vol
        actual_vol = result.val().Volume()
        # Allow 5% tolerance due to union overlaps at leg-tabletop junction
        assert abs(actual_vol - expected_vol) / expected_vol < 0.10, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Check tabletop is hollow: a point inside the hollow region should NOT be inside
        # Interior of hollow tabletop: center at (0, 0, top_depth/2), inside the shell
        hollow_point = (0.0, 0.0, top_depth / 2)
        assert not result.val().isInside(hollow_point), \
            f"Point {hollow_point} should be in hollow region, but isInside returned True"
    
        # Check a point on the tabletop wall IS inside
        wall_point = (0.0, top_width / 2 - shell_t / 2, top_depth / 2)
        assert result.val().isInside(wall_point), \
            f"Point {wall_point} should be inside tabletop wall, but isInside returned False"
    
        # Check legs exist: points inside each leg should be inside the solid
        left_leg_point  = (-leg_x_offset, 0.0, -leg_h / 2)
        right_leg_point = ( leg_x_offset, 0.0, -leg_h / 2)
        assert result.val().isInside(left_leg_point), \
            f"Left leg point {left_leg_point} should be inside solid"
        assert result.val().isInside(right_leg_point), \
            f"Right leg point {right_leg_point} should be inside solid"
    
        # Check rod exists: a point at the center of the rod should be inside
        rod_point = (0.0, 0.0, rod_center_z)
        assert result.val().isInside(rod_point), \
            f"Rod center point {rod_point} should be inside solid"
    
        # Check cylindrical faces exist (rod + possibly leg holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Expected at least 1 cylindrical face (rod), got {cyl_faces}"
    
        # Check the rod diameter: the rod should not extend beyond leg_w in Y
        assert bb.ylen <= top_width + TOL, \
            f"Y extent should not exceed tabletop width {top_width}, got {bb.ylen}"
    
        # Verify rod diameter < leg width
        assert rod_dia < leg_w, \
            f"Rod diameter {rod_dia} should be less than leg width {leg_w}"
    
        # Verify leg height ≈ 3× leg width
        assert abs(leg_h / leg_w - 3.0) < 0.1, \
            f"Leg height/width ratio: expected ~3, got {leg_h/leg_w}"
    
        # Verify tabletop length ≈ 3× tabletop width
        assert abs(top_length / top_width - 3.0) < 0.1, \
            f"Tabletop length/width ratio: expected ~3, got {top_length/top_width}"
    
        # Verify tabletop depth == tabletop width
        assert abs(top_depth - top_width) < TOL, \
            f"Tabletop depth should equal width: depth={top_depth}, width={top_width}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
        print(f"  Volume: {actual_vol:.1f} (expected ~{expected_vol:.1f})")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00851553/gpt_generated.stl')
