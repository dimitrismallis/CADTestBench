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
        table_length  = 1.5
        table_width   = 0.32143
        table_height  = 0.064286
    
        leg_length    = 0.064286
        leg_width     = 0.32143
        leg_height    = 0.47129
    
        # --- Step 1: Table surface centered at origin ---
        # Spans x: [-0.75, 0.75], y: [-0.160715, 0.160715], z: [-0.032143, 0.032143]
        table_surface = cq.Workplane("XY").box(table_length, table_width, table_height)
    
        # --- Step 2: Compute leg positions ---
        # Leg center x: 1/3 of table length from each end
        # Left leg: x_center = -table_length/2 + table_length/3/2 ... 
        # "1/3 of table's length from the respective ends" means the leg center is at
        # distance = table_length/3 from the end => x_left = -table_length/2 + table_length/3
        leg_x_offset = table_length / 2 - table_length / 3   # = 0.75 - 0.5 = 0.25
        # Leg sits below the table surface
        # Table bottom z = -table_height/2 = -0.032143
        # Leg top z = -table_height/2, leg center z = -table_height/2 - leg_height/2
        leg_z_center = -table_height / 2 - leg_height / 2
    
        # --- Step 3: Left leg ---
        left_leg = (
            cq.Workplane("XY")
            .box(leg_length, leg_width, leg_height)
            .translate((-leg_x_offset, 0, leg_z_center))
        )
    
        # --- Step 4: Right leg ---
        right_leg = (
            cq.Workplane("XY")
            .box(leg_length, leg_width, leg_height)
            .translate((leg_x_offset, 0, leg_z_center))
        )
    
        # --- Step 5: Union all parts ---
        result = table_surface.union(left_leg).union(right_leg)
    
        # --- Final object verification ---
        TOL = 1e-3
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box checks
        # X: table dominates => [-0.75, 0.75] => xlen = 1.5
        assert abs(bb.xlen - table_length) < TOL, \
            f"X length: expected {table_length}, got {bb.xlen}"
    
        # Y: table and legs have same width => 0.32143
        assert abs(bb.ylen - table_width) < TOL, \
            f"Y length: expected {table_width}, got {bb.ylen}"
    
        # Z: table top at +table_height/2, leg bottom at -table_height/2 - leg_height
        expected_zlen = table_height / 2 + table_height / 2 + leg_height
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Z extents
        assert abs(bb.zmax - table_height / 2) < TOL, \
            f"Z max: expected {table_height/2}, got {bb.zmax}"
        assert abs(bb.zmin - (-table_height / 2 - leg_height)) < TOL, \
            f"Z min: expected {-(table_height/2 + leg_height)}, got {bb.zmin}"
    
        # Volume check
        table_vol = table_length * table_width * table_height
        leg_vol   = leg_length * leg_width * leg_height
        expected_vol = table_vol + 2 * leg_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Leg x positions: left leg center at -leg_x_offset, right at +leg_x_offset
        # Check that the model extends to ±0.75 in X (table dominates)
        assert abs(bb.xmax - table_length / 2) < TOL, \
            f"X max: expected {table_length/2}, got {bb.xmax}"
        assert abs(bb.xmin - (-table_length / 2)) < TOL, \
            f"X min: expected {-table_length/2}, got {bb.xmin}"
    
        # Symmetry: center of mass should be near (0, 0, ...)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X should be ~0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y should be ~0, got {com.y}"
    
        # Check there are planar faces (table top, bottom, sides, leg faces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count >= 6, \
            f"Expected at least 6 planar faces, got {planar_face_count}"
    
        print(f"Bounding box: x={bb.xlen:.5f}, y={bb.ylen:.5f}, z={bb.zlen:.5f}")
        print(f"Volume: expected={expected_vol:.6f}, actual={actual_vol:.6f}")
        print(f"Center of mass: ({com.x:.5f}, {com.y:.5f}, {com.z:.5f})")
        print(f"Planar faces: {planar_face_count}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00009307/gpt_generated.stl')
