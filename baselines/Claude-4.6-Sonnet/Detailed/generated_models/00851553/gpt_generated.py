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
        top_L = 1.05974       # tabletop length (X)
        top_W = 0.362338      # tabletop width (Y)
        top_H = 0.362338      # tabletop height (Z) = same as width
    
        cut_L = 0.954546      # hollow cut length (X)
        cut_W = 0.261039      # hollow cut width (Y)
        cut_D = 0.314632      # hollow cut depth (Z)
    
        leg_L = 0.041039      # leg length (X)
        leg_W = 0.136796      # leg width (Y)
        leg_H = 0.314632      # leg height (Z)
    
        rod_D = 0.108522      # rod diameter
        rod_R = rod_D / 2.0
    
        # --- Step 1: Create the tabletop solid (upper part) ---
        # Centered at origin in XY, from Z=0 to Z=top_H
        tabletop_solid = cq.Solid.makeBox(top_L, top_W, top_H,
                                           pnt=cq.Vector(-top_L/2, -top_W/2, 0))
    
        # --- Step 2: Create the hollow cut solid ---
        # Cut centered in XY, from Z=(top_H - cut_D) to Z=top_H
        cut_solid = cq.Solid.makeBox(cut_L, cut_W, cut_D,
                                      pnt=cq.Vector(-cut_L/2, -cut_W/2, top_H - cut_D))
    
        # --- Step 3: Subtract cut from tabletop ---
        tabletop_hollow = tabletop_solid.cut(cut_solid)
    
        # --- Step 4: Create left leg solid ---
        left_leg_cx = -(top_L / 2.0 - leg_L / 2.0)
        right_leg_cx = (top_L / 2.0 - leg_L / 2.0)
        leg_cy = 0.0
    
        left_leg_solid = cq.Solid.makeBox(leg_L, leg_W, leg_H,
                                           pnt=cq.Vector(left_leg_cx - leg_L/2,
                                                         leg_cy - leg_W/2,
                                                         -leg_H))
    
        # --- Step 5: Create right leg solid ---
        right_leg_solid = cq.Solid.makeBox(leg_L, leg_W, leg_H,
                                            pnt=cq.Vector(right_leg_cx - leg_L/2,
                                                          leg_cy - leg_W/2,
                                                          -leg_H))
    
        # --- Step 6: Create connecting rod ---
        # Rod runs along X axis between the inner faces of the legs
        rod_length = right_leg_cx - leg_L/2.0 - (left_leg_cx + leg_L/2.0)
        rod_z = -leg_H + rod_R  # near bottom of legs
    
        # Rod: cylinder along X axis, centered at X=0
        rod_solid = cq.Solid.makeCylinder(
            rod_R, rod_length,
            pnt=cq.Vector(-rod_length/2.0, 0, rod_z),
            dir=cq.Vector(1, 0, 0)
        )
    
        # --- Step 7: Union all parts ---
        result_solid = tabletop_hollow.fuse(left_leg_solid).fuse(right_leg_solid).fuse(rod_solid)
    
        # Wrap in Workplane
        result = cq.Workplane("XY").add(result_solid)
    
        # --- Final object verification ---
        TOL = 0.005
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box X: tabletop dominates = top_L
        assert abs(bb.xlen - top_L) < TOL, f"X length: expected {top_L}, got {bb.xlen}"
    
        # Overall bounding box Y: tabletop dominates = top_W
        assert abs(bb.ylen - top_W) < TOL, f"Y length: expected {top_W}, got {bb.ylen}"
    
        # Overall bounding box Z: tabletop (top_H) + legs below (leg_H)
        expected_zlen = top_H + leg_H
        assert abs(bb.zlen - expected_zlen) < TOL, f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Z extents
        assert abs(bb.zmin - (-leg_H)) < TOL, f"Z min: expected {-leg_H}, got {bb.zmin}"
        assert abs(bb.zmax - top_H) < TOL, f"Z max: expected {top_H}, got {bb.zmax}"
    
        # Volume check:
        vol_tabletop_solid = top_L * top_W * top_H
        vol_cut = cut_L * cut_W * cut_D
        vol_legs = 2 * leg_L * leg_W * leg_H
        vol_rod = math.pi * rod_R**2 * rod_length
        expected_vol = vol_tabletop_solid - vol_cut + vol_legs + vol_rod
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical face exists (the rod)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face (rod), got {cyl_faces}"
    
        # Check the hollow: a point inside the cut should be outside the solid
        cut_center_z = top_H - cut_D / 2.0
        inside_cut = result.val().isInside((0.0, 0.0, cut_center_z))
        assert not inside_cut, f"Point inside hollow cut should be outside solid"
    
        # Check that a point in the tabletop wall is inside the solid
        wall_x = top_L / 2.0 - 0.02
        wall_z = top_H - cut_D / 2.0
        inside_wall = result.val().isInside((wall_x, 0.0, wall_z))
        assert inside_wall, f"Point in tabletop wall should be inside solid"
    
        # Check symmetry: center of mass should be near X=0, Y=0
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X should be ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0, got {com.y}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00851553/gpt_generated.stl')
