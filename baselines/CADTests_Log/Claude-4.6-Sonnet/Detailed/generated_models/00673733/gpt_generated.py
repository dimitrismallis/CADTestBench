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
        width = 0.75          # height of cylinder along Y-axis
        diameter = 0.249945
        radius = diameter / 2.0   # 0.1249725
        z_offset = 0.125404   # translation of second cylinder along Z
    
        # --- Step 1: Create first cylinder with axis along Y ---
        # CadQuery cylinder default axis is Z, so we use direct=(0,1,0) to orient along Y
        # centered=True means it's centered at origin along its axis
        cyl1 = cq.Workplane("XY").cylinder(width, radius, direct=(0, 1, 0))
    
        # --- Step 2: Create second cylinder, same dimensions, translated by z_offset along Z ---
        cyl2 = cq.Workplane("XY").cylinder(width, radius, direct=(0, 1, 0)).translate((0, 0, z_offset))
    
        # --- Step 3: Subtract second cylinder from first to form crescent ---
        crescent = cyl1.cut(cyl2)
    
        # --- Step 4: Translate by half the width in negative Y direction ---
        # half width = 0.75 / 2 = 0.375
        half_width = width / 2.0
        result = crescent.translate((0, -half_width, 0))
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Check bounding box
        bb = result.val().BoundingBox()
    
        # After translation by -0.375 in Y, the cylinder (originally centered at Y=0,
        # spanning -0.375 to +0.375 in Y) should now span -0.75 to 0 in Y
        assert abs(bb.ymin - (-width)) < TOL, f"Y min: expected {-width}, got {bb.ymin}"
        assert abs(bb.ymax - 0.0) < TOL, f"Y max: expected 0.0, got {bb.ymax}"
        assert abs(bb.ylen - width) < TOL, f"Y length: expected {width}, got {bb.ylen}"
    
        # X extent should be approximately the diameter (crescent is within original cylinder bounds in X)
        assert bb.xlen <= diameter + TOL, f"X length should be <= diameter {diameter}, got {bb.xlen}"
        assert bb.xlen > 0, f"X length should be positive, got {bb.xlen}"
    
        # Z extent: crescent is cut from +Z side, so zmax < radius, zmin ~ -radius
        assert bb.zlen <= diameter + TOL, f"Z length should be <= diameter {diameter}, got {bb.zlen}"
        assert bb.zlen > 0, f"Z length should be positive, got {bb.zlen}"
        # The crescent opens toward +Z, so zmax should be less than full radius
        assert bb.zmax < radius, f"Z max should be less than radius {radius} (cut from +Z side), got {bb.zmax}"
        # zmin should be approximately -radius (uncut side)
        assert abs(bb.zmin - (-radius)) < TOL, f"Z min: expected ~{-radius}, got {bb.zmin}"
    
        # Volume check: crescent should be less than full cylinder volume
        full_cyl_vol = math.pi * radius**2 * width
        crescent_vol = result.val().Volume()
        assert crescent_vol < full_cyl_vol, f"Crescent volume {crescent_vol} should be less than full cylinder {full_cyl_vol}"
        assert crescent_vol > 0, f"Crescent volume should be positive, got {crescent_vol}"
    
        print(f"Crescent volume: {crescent_vol:.6f}")
        print(f"Full cylinder volume: {full_cyl_vol:.6f}")
        print(f"Bounding box: x=[{bb.xmin:.4f},{bb.xmax:.4f}], y=[{bb.ymin:.4f},{bb.ymax:.4f}], z=[{bb.zmin:.4f},{bb.zmax:.4f}]")
        print(f"Z offset between cylinder centers: {z_offset}, radius: {radius}")
        print(f"Overlap distance: {2*radius - z_offset:.6f}")
    
        # Verify the shape is a crescent (not empty, not full cylinder)
        vol_ratio = crescent_vol / full_cyl_vol
        assert 0.0 < vol_ratio < 1.0, f"Volume ratio should be between 0 and 1, got {vol_ratio}"
    
        # Check center of mass
        com = cq.Shape.centerOfMass(result.val())
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        # COM z should be negative (crescent opens toward +Z, material is on -Z side)
        assert com.z < 0, f"Center of mass Z should be negative (crescent opens toward +Z), got {com.z}"
    
        # COM y: after translation, cylinder spans y=[-0.75, 0.0], so COM y should be at -0.375
        # (midpoint of the Y range, since the crescent is uniform along Y)
        assert abs(com.y - (-half_width)) < TOL * 10, \
            f"COM Y: expected ~{-half_width:.4f}, got {com.y:.4f}"
    
        # COM x should be near 0 (symmetric about X=0)
        assert abs(com.x) < TOL, f"COM X should be ~0 (symmetric), got {com.x}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00673733/gpt_generated.stl')
