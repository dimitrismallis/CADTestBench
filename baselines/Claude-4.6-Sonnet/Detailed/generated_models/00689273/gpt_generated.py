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
        cyl_height = 0.325804   # cylinder width/height
        cyl_diameter = 0.651607
        cyl_radius = cyl_diameter / 2.0  # 0.325804 (approx)
    
        block_length = 0.839006   # along X
        block_width  = 0.201998   # along Y (narrow)
        block_height = 0.065161   # along Z (very short)
    
        # --- Step 1: Create the base cylinder ---
        # Cylinder centered at origin, axis along Z
        # height = cyl_height, radius = cyl_radius
        cylinder = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # Cylinder top face is at Z = cyl_height / 2
        cyl_top_z = cyl_height / 2.0  # 0.162902
    
        # --- Step 2: Create the rectangular block ---
        # The block is centered in X and Y, placed on top of the cylinder
        # Block bottom at cyl_top_z, so block center Z = cyl_top_z + block_height/2
        block_center_z = cyl_top_z + block_height / 2.0
    
        block = (
            cq.Workplane("XY")
            .box(block_length, block_width, block_height, centered=True)
            .translate((0, 0, block_center_z))
        )
    
        # --- Step 3: Union cylinder and block ---
        result = cylinder.union(block)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: block is longer than cylinder diameter
        # block_length = 0.839006 > cyl_diameter = 0.651607
        # So X extent should be block_length
        assert abs(bb.xlen - block_length) < TOL, \
            f"X extent: expected {block_length:.6f}, got {bb.xlen:.6f}"
    
        # Y extent: cylinder diameter is wider than block width
        # cyl_diameter = 0.651607 > block_width = 0.201998
        # So Y extent should be cyl_diameter
        assert abs(bb.ylen - cyl_diameter) < TOL, \
            f"Y extent: expected {cyl_diameter:.6f}, got {bb.ylen:.6f}"
    
        # Z extent: cylinder height + block height
        expected_z = cyl_height + block_height
        assert abs(bb.zlen - expected_z) < TOL, \
            f"Z extent: expected {expected_z:.6f}, got {bb.zlen:.6f}"
    
        # Z min should be at -cyl_height/2
        assert abs(bb.zmin - (-cyl_height / 2.0)) < TOL, \
            f"Z min: expected {-cyl_height/2.0:.6f}, got {bb.zmin:.6f}"
    
        # Z max should be at cyl_height/2 + block_height
        expected_zmax = cyl_height / 2.0 + block_height
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"Z max: expected {expected_zmax:.6f}, got {bb.zmax:.6f}"
    
        # Volume check: cylinder + block (they share a face at the top, minimal overlap)
        cyl_vol = math.pi * cyl_radius**2 * cyl_height
        block_vol = block_length * block_width * block_height
        # The block sits on top of the cylinder, overlap is minimal (just the interface face)
        # For a union, volume = cyl_vol + block_vol - overlap_vol
        # The block bottom face intersects the cylinder top face
        # Overlap volume is approximately the area of intersection * 0 (faces, not volumes)
        # Actually the block is placed exactly on top, so no volumetric overlap
        expected_vol = cyl_vol + block_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical face exists (the cylinder curved surface)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check that the block top face is at the correct Z
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - expected_zmax) < TOL, \
            f"Top face Z: expected {expected_zmax:.6f}, got {top_face_z:.6f}"
    
        # Check center of mass is roughly at X=0, Y=0 (symmetric)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x:.6f}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y:.6f}"
    
        # The block is above the cylinder center, so COM Z should be slightly above 0
        assert com.z > 0, f"Center of mass Z should be above 0, got {com.z:.6f}"
    
        print(f"Bounding box: X={bb.xlen:.6f}, Y={bb.ylen:.6f}, Z={bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected ~{expected_vol:.6f})")
        print(f"Center of mass: ({com.x:.6f}, {com.y:.6f}, {com.z:.6f})")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00689273/gpt_generated.stl')
