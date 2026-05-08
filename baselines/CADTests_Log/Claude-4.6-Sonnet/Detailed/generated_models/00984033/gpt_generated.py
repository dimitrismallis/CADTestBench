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
        length = 1.5
        width = 0.017559       # thin dimension (Y)
        height = 0.546823      # Z dimension
        hole_dia = 0.301003
        hole_radius = hole_dia / 2.0
    
        # Hole positioning (before rotation):
        # "left edge" = min X = -length/2 = -0.75
        # "top edge"  = max Z = height/2 = 0.273412
        left_edge = -length / 2.0
        top_edge = height / 2.0
    
        # First hole center
        h1_x = left_edge + 0.446488
        h1_z = top_edge - 0.050167
    
        # Spacing between holes
        spacing = hole_dia + 0.050167  # 0.351170
    
        h2_x = h1_x + spacing
        h3_x = h2_x + spacing
    
        # --- Step 1: Create base rectangular plate ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Cut three circular holes through the Y direction ---
        result = (
            result
            .faces(">Y").workplane()
            .pushPoints([(h1_x, h1_z), (h2_x, h1_z), (h3_x, h1_z)])
            .hole(hole_dia)
        )
    
        # --- Step 3: Rotate 180 degrees around Z-axis ---
        result = result.rotate((0, 0, 0), (0, 0, 1), 180)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box should remain the same after 180° Z rotation (symmetric in X and Y)
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width) < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check:
        # The holes are drilled through Y (width=0.017559).
        # Hole diameter = 0.301003, radius = 0.150502.
        # Hole center Z = top_edge - 0.050167 = 0.273412 - 0.050167 = 0.223244
        # The hole circle extends from Z = 0.223244 - 0.150502 = 0.072742
        #                              to Z = 0.223244 + 0.150502 = 0.373746
        # Plate top Z = 0.273412, so the hole is clipped at the top.
        # Distance from hole center to top clip line: d = 0.050167
        # Area of circular cap above top edge (excluded from plate):
        #   A_cap = r^2 * arccos(d/r) - d * sqrt(r^2 - d^2)
        r = hole_radius
        d = 0.050167  # distance from hole center to top edge
        A_cap = r**2 * math.acos(d / r) - d * math.sqrt(r**2 - d**2)
        A_full = math.pi * r**2
        A_within = A_full - A_cap  # area of hole cross-section within plate
    
        # No clipping in X or bottom Z directions (verified by geometry)
        vol_removed_per_hole = A_within * width
        plate_vol = length * width * height
        expected_vol = plate_vol - 3 * vol_removed_per_hole
    
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces: 3 holes → 3 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 3, f"Cylindrical faces: expected 3, got {cyl_faces}"
    
        # Check that holes exist: points at hole centers should be outside the solid (they're air)
        # After 180° Z rotation, hole centers: (-h1_x, 0, h1_z), (-h2_x, 0, h1_z), (-h3_x, 0, h1_z)
        for hx_orig in [h1_x, h2_x, h3_x]:
            hx_rot = -hx_orig
            pt = (hx_rot, 0.0, h1_z)
            inside = solid.isInside(pt, tolerance=1e-5)
            assert not inside, f"Point {pt} should be inside hole (not solid), but isInside={inside}"
    
        # Total face count should be > 6 (plate has holes)
        total_faces = result.faces().size()
        assert total_faces > 6, f"Total faces should be > 6 (has holes), got {total_faces}"
    
        # Center of mass: holes are near the top (positive Z before rotation, same after 180° Z rotation
        # since Z is unchanged by rotation about Z-axis). Removing material from top shifts CoM toward -Z.
        # CoM Z should be negative (shifted down from 0 due to top holes) and within plate Z bounds.
        com = cq.Shape.centerOfMass(solid)
        assert com.z < 0, f"Center of mass Z should be negative (holes near top remove material), got {com.z}"
        assert com.z > -height / 2.0, f"Center of mass Z should be within plate bounds, got {com.z}"
    
        # CoM X should be near 0 (plate is symmetric in X after 180° rotation)
        # After rotation: hole X positions are (-h1_x, -h2_x, -h3_x)
        # These are not symmetric about X=0, so CoM X will be offset
        # Just verify CoM X is within plate X bounds
        assert abs(com.x) < length / 2.0, f"Center of mass X should be within plate bounds, got {com.x}"
    
        # CoM Y should be ~0 (symmetric in Y)
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0, got {com.y}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"Total faces: {total_faces}")
        print(f"Center of mass: ({com.x:.6f}, {com.y:.6f}, {com.z:.6f})")
        print(f"Hole centers after rotation: ({-h1_x:.4f}, 0, {h1_z:.4f}), ({-h2_x:.4f}, 0, {h1_z:.4f}), ({-h3_x:.4f}, 0, {h1_z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00984033/gpt_generated.stl')
