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
        # Parameters
        base_length = 0.75      # X dimension of the U
        u_width = 0.3           # Y dimension (depth of U walls)
        base_height = 0.15      # Z height of the base/bottom of U
        total_height = 0.45     # Total Z height of the bracket
        wall_thickness = 0.075  # thickness of U side walls
    
        # The closing rectangle is wider than U's width by 0.45
        # closing_width = u_width + 0.45 = 0.75
        closing_width = u_width + 0.45  # = 0.75
        flange_thickness = base_height  # same as base thickness = 0.15
    
        # Wall height = total_height (walls run full height)
        # Flange sits at top of walls, but within total_height
        # So: base (0 to 0.15) + walls (0 to 0.45) + flange at top (0.30 to 0.45)
        # Flange occupies the top 0.15 of the total 0.45 height
        flange_z_start = total_height - flange_thickness  # = 0.30
    
        # --- Step 1: Create the U-shaped base (bottom horizontal bar) ---
        # Bottom of U: full base_length × u_width × base_height
        base = cq.Workplane("XY").box(base_length, u_width, base_height,
                                       centered=(True, True, False))
    
        # --- Step 2: Create left wall of U ---
        left_wall = cq.Workplane("XY").box(wall_thickness, u_width, total_height,
                                            centered=(True, True, False))
        left_wall = left_wall.translate((-base_length/2 + wall_thickness/2, 0, 0))
    
        # --- Step 3: Create right wall of U ---
        right_wall = cq.Workplane("XY").box(wall_thickness, u_width, total_height,
                                             centered=(True, True, False))
        right_wall = right_wall.translate((base_length/2 - wall_thickness/2, 0, 0))
    
        # --- Step 4: Create the closing rectangle (top flange) ---
        # Wider than U's width (0.3) by 0.45 → total Y = 0.75
        # Placed at the top portion of the bracket
        top_flange = cq.Workplane("XY").box(base_length, closing_width, flange_thickness,
                                             centered=(True, True, False))
        top_flange = top_flange.translate((0, 0, flange_z_start))
    
        # --- Step 5: Union all parts ---
        result = base.union(left_wall).union(right_wall).union(top_flange)
    
        # --- Final object verification ---
        TOL = 0.01
        bb = result.val().BoundingBox()
    
        # Check overall bounding box
        assert abs(bb.xlen - base_length) < TOL, \
            f"X length: expected {base_length}, got {bb.xlen}"
        assert abs(bb.ylen - closing_width) < TOL, \
            f"Y length: expected {closing_width}, got {bb.ylen}"
        assert abs(bb.zlen - total_height) < TOL, \
            f"Z length: expected {total_height}, got {bb.zlen}"
    
        # Check Z extents
        assert abs(bb.zmin - 0) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - total_height) < TOL, \
            f"Z max: expected {total_height}, got {bb.zmax}"
    
        # Check X extents (centered)
        assert abs(bb.xmin - (-base_length/2)) < TOL, \
            f"X min: expected {-base_length/2}, got {bb.xmin}"
        assert abs(bb.xmax - (base_length/2)) < TOL, \
            f"X max: expected {base_length/2}, got {bb.xmax}"
    
        # Check Y extents (centered)
        assert abs(bb.ymin - (-closing_width/2)) < TOL, \
            f"Y min: expected {-closing_width/2}, got {bb.ymin}"
        assert abs(bb.ymax - (closing_width/2)) < TOL, \
            f"Y max: expected {closing_width/2}, got {bb.ymax}"
    
        # Volume check:
        # Base: 0.75 × 0.3 × 0.15
        # Left wall: 0.075 × 0.3 × 0.45 (full height)
        # Right wall: 0.075 × 0.3 × 0.45 (full height)
        # Top flange: 0.75 × 0.75 × 0.15 (at z=0.30 to 0.45)
        # Overlaps:
        #   base ∩ left_wall: 0.075 × 0.3 × 0.15
        #   base ∩ right_wall: 0.075 × 0.3 × 0.15
        #   flange ∩ left_wall: 0.075 × 0.3 × 0.15
        #   flange ∩ right_wall: 0.075 × 0.3 × 0.15
        # No triple overlaps (base and flange don't overlap)
    
        base_vol = base_length * u_width * base_height          # 0.75*0.3*0.15 = 0.03375
        wall_vol = wall_thickness * u_width * total_height      # 0.075*0.3*0.45 = 0.010125 each
        flange_vol = base_length * closing_width * flange_thickness  # 0.75*0.75*0.15 = 0.084375
    
        # Overlaps (inclusion-exclusion)
        base_wall_overlap = wall_thickness * u_width * base_height   # 0.075*0.3*0.15 = 0.003375 each
        flange_wall_overlap = wall_thickness * u_width * flange_thickness  # 0.075*0.3*0.15 = 0.003375 each
    
        expected_vol = (base_vol 
                        + 2 * wall_vol 
                        + flange_vol 
                        - 2 * base_wall_overlap 
                        - 2 * flange_wall_overlap)
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that the U-channel interior is open (between walls, above base, below flange)
        # Point in the middle of the U channel
        mid_x = 0.0
        mid_y = 0.0
        mid_z = 0.22  # between base_height=0.15 and flange_z_start=0.30
        inner_point = cq.Vector(mid_x, mid_y, mid_z)
        is_inside = result.val().isInside(inner_point)
        assert not is_inside, \
            f"Interior U-channel point should be outside solid, but isInside={is_inside}"
    
        # Check that a point in the base is inside
        base_point = cq.Vector(0, 0, 0.075)
        assert result.val().isInside(base_point), \
            "Base center point should be inside solid"
    
        # Check that a point in the top flange is inside
        flange_point = cq.Vector(0, 0, flange_z_start + flange_thickness/2)
        assert result.val().isInside(flange_point), \
            "Top flange center point should be inside solid"
    
        # Check that a point in the left wall (outside U width) is inside
        left_wall_point = cq.Vector(-base_length/2 + wall_thickness/2, 0, 0.22)
        assert result.val().isInside(left_wall_point), \
            "Left wall point should be inside solid"
    
        # Check that a point in the right wall (outside U width) is inside
        right_wall_point = cq.Vector(base_length/2 - wall_thickness/2, 0, 0.22)
        assert result.val().isInside(right_wall_point), \
            "Right wall point should be inside solid"
    
        # Check the U-channel is open on the sides (Y direction)
        # A point outside the U width but within the bracket height (below flange)
        outside_y_point = cq.Vector(0, closing_width/2 - 0.01, 0.22)
        is_outside_inside = result.val().isInside(outside_y_point)
        assert not is_outside_inside, \
            f"Point outside U-width should not be inside solid at mid-height"
    
        print(f"Bounding box: X={bb.xlen:.4f}, Y={bb.ylen:.4f}, Z={bb.zlen:.4f}")
        print(f"Volume: expected={expected_vol:.6f}, actual={actual_vol:.6f}")
        print(f"Closing width: {closing_width:.4f} (u_width {u_width} + 0.45)")
        print(f"Total height: {total_height:.4f} (base {base_height} + walls up to {total_height})")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00034256/gpt_generated.stl')
