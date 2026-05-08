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
        prism_L = 1.0
        prism_W = 0.1
        prism_H = 1.25
    
        hole_L = 0.5
        hole_W = 0.1   # matches prism width (through cut)
        hole_H = 0.075
        bottom_padding = 0.25
    
        # --- Step 1: Create the base rectangular prism (centered at origin) ---
        # Box is centered: X in [-0.5, 0.5], Y in [-0.05, 0.05], Z in [-0.625, 0.625]
        result = cq.Workplane("XY").box(prism_L, prism_W, prism_H)
    
        # --- Step 2: Create and cut the rectangular hole ---
        # Hole is centered horizontally (X=0), full width in Y (through cut),
        # bottom of hole at z = -prism_H/2 + bottom_padding = -0.625 + 0.25 = -0.375
        # Center of hole in Z = -0.375 + hole_H/2 = -0.375 + 0.0375 = -0.3375
        hole_z_center = -prism_H / 2 + bottom_padding + hole_H / 2
        # hole_z_center = -0.625 + 0.25 + 0.0375 = -0.3375
    
        hole = cq.Workplane("XY").box(hole_L, hole_W, hole_H).translate((0, 0, hole_z_center))
    
        result = result.cut(hole)
    
        # --- Step 3: Translate the entire structure slightly for better positioning ---
        # Move so the base sits at z=0 and is offset in X and Y
        result = result.translate((0.5, 0.5, prism_H / 2))
        # After translation: prism occupies X=[0,1], Y=[0.45,0.55], Z=[0,1.25]
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks (after translation)
        # X: 0.5 - 0.5 = 0.0 to 0.5 + 0.5 = 1.0
        assert abs(bb.xmin - 0.0) < TOL, f"xmin expected 0.0, got {bb.xmin}"
        assert abs(bb.xmax - 1.0) < TOL, f"xmax expected 1.0, got {bb.xmax}"
        assert abs(bb.xlen - prism_L) < TOL, f"X length expected {prism_L}, got {bb.xlen}"
    
        # Y: 0.5 - 0.05 = 0.45 to 0.5 + 0.05 = 0.55
        assert abs(bb.ymin - 0.45) < TOL, f"ymin expected 0.45, got {bb.ymin}"
        assert abs(bb.ymax - 0.55) < TOL, f"ymax expected 0.55, got {bb.ymax}"
        assert abs(bb.ylen - prism_W) < TOL, f"Y length expected {prism_W}, got {bb.ylen}"
    
        # Z: 0 to 1.25
        assert abs(bb.zmin - 0.0) < TOL, f"zmin expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - prism_H) < TOL, f"zmax expected {prism_H}, got {bb.zmax}"
        assert abs(bb.zlen - prism_H) < TOL, f"Z length expected {prism_H}, got {bb.zlen}"
    
        # Volume check: prism volume minus hole volume
        prism_vol = prism_L * prism_W * prism_H
        hole_vol = hole_L * hole_W * hole_H
        expected_vol = prism_vol - hole_vol
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) < TOL, \
            f"Volume expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check hole exists: a point inside the hole region should be OUTSIDE the solid
        # Hole center after translation: (0.5, 0.5, hole_z_center + prism_H/2)
        hole_center_z_world = hole_z_center + prism_H / 2
        hole_center_x_world = 0.5
        hole_center_y_world = 0.5
        hole_point = (hole_center_x_world, hole_center_y_world, hole_center_z_world)
        assert not solid.isInside(hole_point), \
            f"Point {hole_point} should be inside the hole (outside solid), but it's inside"
    
        # Check a point in the solid body (above the hole) is inside
        solid_point = (0.5, 0.5, 0.8)  # well above the hole region
        assert solid.isInside(solid_point), \
            f"Point {solid_point} should be inside the solid, but it's not"
    
        # Check a point below the hole (in the bottom padding region) is inside
        bottom_point = (0.5, 0.5, 0.1)  # z=0.1, within bottom padding (0 to 0.25)
        assert solid.isInside(bottom_point), \
            f"Point {bottom_point} should be inside the solid (bottom padding), but it's not"
    
        # Face count: a box with a rectangular through-hole
        # Prism has 6 faces, hole removes material creating additional faces
        # The hole is a through-cut in Y (full width), so it creates 4 new faces (top, bottom, left, right of hole)
        # and modifies the two Y-facing faces (front and back) of the prism
        # Total planar faces: 6 (original) - 2 (Y faces modified) + 2 (Y faces with hole cutout) + 4 (hole walls) = 10
        # But the Y faces now have a rectangular cutout, making them non-simple
        # Let's just check we have more than 6 faces
        face_count = result.faces().size()
        assert face_count >= 8, f"Expected at least 8 faces, got {face_count}"
    
        print(f"✓ Bounding box: X=[{bb.xmin:.3f},{bb.xmax:.3f}], Y=[{bb.ymin:.3f},{bb.ymax:.3f}], Z=[{bb.zmin:.3f},{bb.zmax:.3f}]")
        print(f"✓ Volume: expected={expected_vol:.6f}, actual={actual_vol:.6f}")
        print(f"✓ Face count: {face_count}")
        print(f"✓ Hole center (world): {hole_point}")
        print(f"✓ All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00521025/gpt_generated.stl')
