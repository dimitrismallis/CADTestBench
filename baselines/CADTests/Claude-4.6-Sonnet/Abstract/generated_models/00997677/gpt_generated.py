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
        base_length = 100.0   # X dimension of base plate
        base_width  = 60.0    # Y dimension of base plate
        base_height = 5.0     # Z (thickness) of base plate
    
        col_length  = 20.0    # X dimension of each column
        col_width   = 60.0    # Y dimension of each column (full width)
        col_height  = 40.0    # Z (height) of each column
    
        # Columns are placed symmetrically at each end along X.
        # col_x_offset: distance from center to column center along X
        col_x_offset = (base_length / 2) - (col_length / 2)  # = 40.0
    
        # --- Step 1: Create the base plate centered at origin ---
        # Base plate: 100 x 60 x 5, centered at (0, 0, 0)
        # Occupies z = -base_height/2 to +base_height/2
        base = cq.Workplane("XY").box(base_length, base_width, base_height)
    
        # --- Step 2: Create left column ---
        # Column sits on top of base plate: z from base_height/2 to base_height/2 + col_height
        # Center of column in Z: base_height/2 + col_height/2
        col_z_center = base_height / 2 + col_height / 2
        left_col = (
            cq.Workplane("XY")
            .box(col_length, col_width, col_height,
                 centered=(True, True, True))
            .translate((-col_x_offset, 0, col_z_center))
        )
    
        # --- Step 3: Create right column ---
        right_col = (
            cq.Workplane("XY")
            .box(col_length, col_width, col_height,
                 centered=(True, True, True))
            .translate((col_x_offset, 0, col_z_center))
        )
    
        # --- Step 4: Union all three parts ---
        result = base.union(left_col).union(right_col)
    
        # --- Final object verification ---
        TOL = 0.1
    
        solid = result.findSolid()
        bb = solid.BoundingBox()
    
        # Overall bounding box
        # Z spans from -base_height/2 to base_height/2 + col_height
        expected_zlen = base_height + col_height  # 5 + 40 = 45
        assert abs(bb.xlen - base_length) < TOL, \
            f"X length: expected {base_length}, got {bb.xlen}"
        assert abs(bb.ylen - base_width) < TOL, \
            f"Y length: expected {base_width}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check:
        # Base plate volume + two column volumes (columns sit on top, no overlap)
        vol_base = base_length * base_width * base_height
        vol_col  = col_length * col_width * col_height
        expected_vol = vol_base + 2 * vol_col
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # No cylindrical faces (all geometry is rectangular)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, \
            f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Check symmetry: center of mass should be at x=0, y=0
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, \
            f"Center of mass Y: expected 0, got {com.y}"
    
        # Check that columns protrude above the base plate top face
        base_top_z = base_height / 2
        assert bb.zmax > base_top_z + TOL, \
            f"Columns should protrude above base plate: zmax={bb.zmax}"
    
        # Check that a point inside the left column is inside the solid
        left_col_point = (-col_x_offset, 0, base_top_z + col_height / 2)
        assert solid.isInside(left_col_point), \
            f"Point {left_col_point} should be inside left column"
    
        # Check that a point inside the right column is inside the solid
        right_col_point = (col_x_offset, 0, base_top_z + col_height / 2)
        assert solid.isInside(right_col_point), \
            f"Point {right_col_point} should be inside right column"
    
        # Check that a point in the middle (between columns, above base) is NOT inside
        mid_point = (0, 0, base_top_z + col_height / 2)
        assert not solid.isInside(mid_point), \
            f"Point {mid_point} should NOT be inside solid (gap between columns)"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997677/gpt_generated.stl')
