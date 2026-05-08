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
        diameter = 0.375
        radius = diameter / 2.0        # 0.1875
        height = 0.691189
        # "length of 0.208765 along the top" = distance along diameter from cut to far edge
        top_length = 0.208765
    
        # --- Step 1: Create the base cylinder centered at origin ---
        # Cylinder axis along Z, centered at origin: z in [-height/2, +height/2]
        cyl = cq.Workplane("XY").cylinder(height, radius)
    
        z_bot = -height / 2.0   # -0.345595
        z_top = +height / 2.0   # +0.345595
    
        # --- Step 2: Define the cutting plane ---
        # The cut plane goes from x = +radius at z=z_bot (one edge of base)
        # to x = radius - top_length at z=z_top
        # x_cut_top = radius - top_length = 0.1875 - 0.208765 = -0.021265
        x_cut_bot = radius                          # +0.1875
        x_cut_top = radius - top_length             # -0.021265
    
        # Tilt angle from vertical:
        tilt_angle_rad = math.atan2(x_cut_bot - x_cut_top, height)
        tilt_angle_deg = math.degrees(tilt_angle_rad)
        # ≈ atan(0.208765 / 0.691189) ≈ 16.84°
    
        # --- Step 3: Build the cutting solid as a large box ---
        # The cutting plane at z=0 (mid-height):
        x_cut_mid = (x_cut_bot + x_cut_top) / 2.0  # ≈ 0.083118
    
        # Create a large box with its left face at x=0 (before rotation/translation)
        # Box extends in +X direction (the material to be removed)
        big = 2.0  # large enough to cover the cylinder
    
        # Box: x in [0, big], y in [-big, big], z in [-big, big]
        cutter = (
            cq.Workplane("XY")
            .box(big, big * 2, big * 2, centered=False)
            .translate((0, -big, -big))
        )
    
        # Rotate the cutter about Y axis by tilt_angle_deg
        cutter = cutter.rotate((0, 0, 0), (0, 1, 0), tilt_angle_deg)
    
        # Translate so the cutting face passes through (x_cut_mid, 0, 0)
        cutter = cutter.translate((x_cut_mid, 0, 0))
    
        # --- Step 4: Perform the cut ---
        result = cyl.cut(cutter)
    
        # --- Step 5: Rotate for proper orientation ---
        # Rotate -90 degrees about X axis so cylinder axis becomes horizontal
        result = result.rotate((0, 0, 0), (1, 0, 0), -90)
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # After -90° rotation about X: (x,y,z) -> (x, z, -y)
        # X extent: diameter
        assert abs(bb.xlen - diameter) < TOL, \
            f"X extent: expected {diameter:.4f}, got {bb.xlen:.4f}"
    
        # Y extent: original Z range = height
        assert abs(bb.ylen - height) < TOL, \
            f"Y extent: expected {height:.4f}, got {bb.ylen:.4f}"
    
        # Z extent: original Y range = diameter
        assert abs(bb.zlen - diameter) < TOL, \
            f"Z extent: expected {diameter:.4f}, got {bb.zlen:.4f}"
    
        # Volume check: numerically integrate the removed volume
        full_vol = math.pi * radius**2 * height
    
        n_steps = 10000
        z_vals = np.linspace(z_bot, z_top, n_steps)
        dz = height / (n_steps - 1)
        vol_removed = 0.0
        for z in z_vals:
            d = x_cut_bot + (x_cut_top - x_cut_bot) * (z - z_bot) / height
            if d >= radius:
                seg_area = 0.0
            elif d <= -radius:
                seg_area = math.pi * radius**2
            else:
                seg_area = radius**2 * math.acos(d / radius) - d * math.sqrt(radius**2 - d**2)
            vol_removed += seg_area * dz
        expected_vol = full_vol - vol_removed
    
        actual_vol = solid.Volume()
        ratio_removed = vol_removed / full_vol
    
        print(f"Full volume: {full_vol:.6f}")
        print(f"Volume removed (numerical): {vol_removed:.6f}")
        print(f"Expected volume: {expected_vol:.6f}")
        print(f"Actual volume: {actual_vol:.6f}")
        print(f"Ratio removed: {ratio_removed:.4f}")
    
        # The actual volume should match the numerically expected volume closely
        assert abs(actual_vol - expected_vol) / full_vol < 0.05, \
            f"Volume mismatch: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # The cut removes approximately 1/3 of material (description says "approximately one-third")
        # Allow range 0.20 to 0.45 to accommodate the specific geometry
        assert 0.20 < ratio_removed < 0.45, \
            f"Expected ~1/3 removed (20%-45%), got {ratio_removed:.4f} removed"
    
        # Check planar faces: at least 3 (top ellipse/circle, bottom circle, flat cut face)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 3, \
            f"Expected at least 3 planar faces, got {planar_faces}"
    
        # Check cylindrical face exists
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check single solid
        n_solids = result.solids().size()
        assert n_solids == 1, \
            f"Expected 1 solid, got {n_solids}"
    
        # Check center of mass is offset (asymmetric cut removed +X material)
        com = cq.Shape.centerOfMass(solid)
        # After -90° rotation about X, original X stays X
        # Cut removed +X material so COM.x < 0
        assert com.x < 0, \
            f"COM.x should be negative (cut removed +X side), got {com.x:.4f}"
    
        print(f"Tilt angle: {tilt_angle_deg:.4f} degrees")
        print(f"x_cut_bot: {x_cut_bot:.6f}, x_cut_top: {x_cut_top:.6f}")
        print(f"Bounding box: x={bb.xlen:.4f}, y={bb.ylen:.4f}, z={bb.zlen:.4f}")
        print(f"Planar faces: {planar_faces}, Cylindrical faces: {cyl_faces}")
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00036518/gpt_generated.stl')
