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
        table_length = 90.0   # X direction
        table_width  = 30.0   # Y direction
        table_thick  = 5.0    # Z direction (tabletop thickness)
        leg_length   = table_length / 3.0  # 30.0, along X
        leg_width    = table_width         # 30.0, along Y (same as table)
        leg_height   = table_width         # 30.0, extruded downward (same as table width)
    
        # --- Step 1: Create the table surface (tabletop) ---
        # Centered at origin: X in [-45, 45], Y in [-15, 15], Z in [0, 5]
        tabletop = (
            cq.Workplane("XY")
            .box(table_length, table_width, table_thick,
                 centered=(True, True, False))
        )
    
        # --- Step 2: Create the left leg ---
        # Left leg: X in [-45, -15], Y in [-15, 15], Z in [-30, 0]
        # Center of left leg: X = -30, Y = 0, Z = -15
        left_leg = (
            cq.Workplane("XY")
            .box(leg_length, leg_width, leg_height,
                 centered=(True, True, False))
            .translate((-table_length / 2.0 + leg_length / 2.0, 0, -leg_height))
        )
    
        # --- Step 3: Create the right leg ---
        # Right leg: X in [15, 45], Y in [-15, 15], Z in [-30, 0]
        # Center of right leg: X = +30, Y = 0, Z = -15
        right_leg = (
            cq.Workplane("XY")
            .box(leg_length, leg_width, leg_height,
                 centered=(True, True, False))
            .translate((table_length / 2.0 - leg_length / 2.0, 0, -leg_height))
        )
    
        # --- Step 4: Union all parts ---
        result = tabletop.union(left_leg).union(right_leg)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box
        # X: -45 to +45 → xlen = 90
        assert abs(bb.xlen - table_length) < TOL, \
            f"X length: expected {table_length}, got {bb.xlen}"
        # Y: -15 to +15 → ylen = 30
        assert abs(bb.ylen - table_width) < TOL, \
            f"Y length: expected {table_width}, got {bb.ylen}"
        # Z: -30 to +5 → zlen = 35
        expected_zlen = table_thick + leg_height
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Z extents
        assert abs(bb.zmin - (-leg_height)) < TOL, \
            f"Z min: expected {-leg_height}, got {bb.zmin}"
        assert abs(bb.zmax - table_thick) < TOL, \
            f"Z max: expected {table_thick}, got {bb.zmax}"
    
        # Volume check
        # Tabletop volume
        vol_top = table_length * table_width * table_thick
        # Each leg volume
        vol_leg = leg_length * leg_width * leg_height
        # The legs share the same Y range as the tabletop and sit directly below it
        # No overlap between tabletop and legs (legs are at Z<0, top is at Z>=0)
        expected_vol = vol_top + 2 * vol_leg
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Check symmetry: center of mass should be at X=0, Y=0
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, \
            f"Center of mass Y: expected 0, got {com.y}"
    
        # Check that legs are present on left and right sides
        # Left leg center should be at X = -30
        # Right leg center should be at X = +30
        # Verify by checking that material exists at those X positions
        solid = result.val()
        left_leg_center  = (-30.0, 0.0, -15.0)
        right_leg_center = ( 30.0, 0.0, -15.0)
        assert solid.isInside(left_leg_center), \
            f"Left leg center {left_leg_center} should be inside the solid"
        assert solid.isInside(right_leg_center), \
            f"Right leg center {right_leg_center} should be inside the solid"
    
        # Verify the middle gap (no leg in the center bottom region)
        middle_bottom = (0.0, 0.0, -15.0)
        assert not solid.isInside(middle_bottom), \
            f"Middle bottom {middle_bottom} should NOT be inside the solid (gap between legs)"
    
        # Verify tabletop top surface exists at Z = table_thick
        top_faces = result.faces(">Z")
        assert top_faces.size() >= 1, "Should have at least one top face"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00009307/gpt_generated.stl')
