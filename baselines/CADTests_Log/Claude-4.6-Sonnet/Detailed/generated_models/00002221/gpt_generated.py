import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # Dimensions
        length = 0.0625   # short dimension
        width  = 0.75     # long dimension (elongated edge)
        height = 0.0034   # thickness
    
        # --- Step 1: Floor rectangle (horizontal, lying flat in XY plane) ---
        # Dimensions: length(X) x width(Y) x height(Z), centered at origin
        # Floor spans: X[-0.03125, 0.03125], Y[-0.375, 0.375], Z[-0.0017, 0.0017]
        floor = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Wall rectangle (vertical, perpendicular to floor) ---
        # The wall shares the elongated edge (Y-direction, 0.75 long) with the floor.
        # Wall orientation: thickness(height=0.0034) in X, width(0.75) in Y, length(0.0625) in Z
        # Wall is placed at the right edge of the floor (x = +length/2 = 0.03125),
        # and extends from the floor bottom (Z = -height/2) upward by length (0.0625).
        #
        # Wall center X: length/2 + height/2 = 0.03125 + 0.0017 = 0.03295
        # Wall center Z: -height/2 + length/2 = -0.0017 + 0.03125 = 0.02955
        # Wall spans: X[0.03125, 0.0346], Y[-0.375, 0.375], Z[-0.0017, 0.0608]
        # The wall LEFT face (X=0.03125) coincides with the floor RIGHT face (X=0.03125)
        # → they share a face but have NO volumetric overlap.
    
        wall_x_center = length / 2 + height / 2        # 0.03295
        wall_z_center = -height / 2 + length / 2       # 0.02955
    
        wall = (
            cq.Workplane("XY")
            .box(height, width, length)   # thickness(X) x width(Y) x length(Z)
            .translate((wall_x_center, 0, wall_z_center))
        )
    
        # --- Step 3: Union floor and wall into one solid ---
        result = floor.union(wall)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Overall bounding box
        bb = result.val().BoundingBox()
    
        # X: floor [-0.03125, 0.03125], wall [0.03125, 0.0346] → total [-0.03125, 0.0346]
        expected_xmin = -length / 2
        expected_xmax =  length / 2 + height
        # Y: symmetric about 0
        expected_ymin = -width / 2
        expected_ymax =  width / 2
        # Z: floor bottom at -height/2, wall top at -height/2 + length
        expected_zmin = -height / 2
        expected_zmax = -height / 2 + length
    
        assert abs(bb.xmin - expected_xmin) < TOL, \
            f"xmin: expected {expected_xmin:.6f}, got {bb.xmin:.6f}"
        assert abs(bb.xmax - expected_xmax) < TOL, \
            f"xmax: expected {expected_xmax:.6f}, got {bb.xmax:.6f}"
        assert abs(bb.ymin - expected_ymin) < TOL, \
            f"ymin: expected {expected_ymin:.6f}, got {bb.ymin:.6f}"
        assert abs(bb.ymax - expected_ymax) < TOL, \
            f"ymax: expected {expected_ymax:.6f}, got {bb.ymax:.6f}"
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"zmin: expected {expected_zmin:.6f}, got {bb.zmin:.6f}"
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"zmax: expected {expected_zmax:.6f}, got {bb.zmax:.6f}"
    
        # Bounding box lengths
        expected_xlen = length + height   # 0.0625 + 0.0034 = 0.0659
        expected_ylen = width             # 0.75
        expected_zlen = length            # 0.0625 (wall height, floor is within this range)
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"xlen: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"ylen: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"zlen: expected {expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Volume: floor and wall share only a face (no volumetric overlap),
        # so total volume = vol_floor + vol_wall exactly.
        vol_floor    = length * width * height   # 0.0625 * 0.75 * 0.0034
        vol_wall     = height * width * length   # 0.0034 * 0.75 * 0.0625
        expected_vol = vol_floor + vol_wall      # = 2 * 0.00015938 = 0.00031875
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.8f}, got {actual_vol:.8f}"
    
        # The model should be a single solid after union
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Symmetry: center of mass should be symmetric about Y=0
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.y) < TOL, \
            f"Center of mass Y should be 0 (symmetric), got {com.y}"
    
        # Verify perpendicular faces exist (confirming right-angle connection):
        # Floor bottom face (normal -Z)
        assert result.faces("-Z").size() >= 1, \
            "Expected at least one face with -Z normal (floor bottom)"
        # Wall outer face (normal +X)
        assert result.faces("+X").size() >= 1, \
            "Expected at least one face with +X normal (wall outer)"
        # Wall top face (normal +Z)
        assert result.faces("+Z").size() >= 1, \
            "Expected at least one face with +Z normal (wall top)"
    
        # Verify the inner corner: a point inside the floor should be inside the solid
        floor_interior = (0.0, 0.0, 0.0)
        assert result.val().isInside(floor_interior), \
            f"Point {floor_interior} should be inside the solid (floor region)"
    
        # Verify a point inside the wall should be inside the solid
        wall_interior = (wall_x_center, 0.0, wall_z_center)
        assert result.val().isInside(wall_interior), \
            f"Point {wall_interior} should be inside the solid (wall region)"
    
        print("All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.6f}, Y={bb.ylen:.6f}, Z={bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.8f} (expected {expected_vol:.8f})")
        print(f"Center of mass: ({com.x:.6f}, {com.y:.6f}, {com.z:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00002221/gpt_generated.stl')
