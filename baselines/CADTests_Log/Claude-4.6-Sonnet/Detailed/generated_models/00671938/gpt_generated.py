import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        height = 0.75
        diameter = 0.419231
        radius = diameter / 2  # 0.2096155
    
        # Centers in XY plane (z is handled by cylinder placement)
        cx1, cy1 = -0.09259, -0.022198
        cx2, cy2 =  0.082574, 0.01872
    
        # --- Step 1: Create first cylinder centered at (cx1, cy1, height/2) ---
        cyl1 = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(cx1, cy1, 0))
            .circle(radius)
            .extrude(height)
        )
    
        # --- Step 2: Create second cylinder centered at (cx2, cy2, height/2) ---
        cyl2 = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(cx2, cy2, 0))
            .circle(radius)
            .extrude(height)
        )
    
        # --- Step 3: Union the two cylinders ---
        result = cyl1.union(cyl2)
    
        # --- Final object verification ---
        TOL = 0.001
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box Z: should span from 0 to height
        assert abs(bb.zmin) < TOL, f"Z min expected ~0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"Z max expected {height}, got {bb.zmax}"
        assert abs(bb.zlen - height) < TOL, f"Z length expected {height}, got {bb.zlen}"
    
        # Bounding box X: should span from cx1-radius to cx2+radius
        expected_xmin = cx1 - radius  # -0.09259 - 0.2096155 = -0.3022055
        expected_xmax = cx2 + radius  # 0.082574 + 0.2096155 = 0.2921895
        assert abs(bb.xmin - expected_xmin) < TOL, f"X min expected {expected_xmin:.4f}, got {bb.xmin:.4f}"
        assert abs(bb.xmax - expected_xmax) < TOL, f"X max expected {expected_xmax:.4f}, got {bb.xmax:.4f}"
    
        # Bounding box Y: should span from cy1-radius to cy2+radius
        expected_ymin = cy1 - radius  # -0.022198 - 0.2096155 = -0.2317935 (cy1 is more negative)
        expected_ymax = cy2 + radius  # 0.01872 + 0.2096155 = 0.2283355
        # cy1 - radius vs cy2 - radius: cy1=-0.022198, cy2=0.01872 → cy1-r is more negative
        assert abs(bb.ymin - expected_ymin) < TOL, f"Y min expected {expected_ymin:.4f}, got {bb.ymin:.4f}"
        assert abs(bb.ymax - expected_ymax) < TOL, f"Y max expected {expected_ymax:.4f}, got {bb.ymax:.4f}"
    
        # Volume: union of two cylinders = V1 + V2 - V_intersection
        # V1 = V2 = pi * r^2 * h
        single_vol = math.pi * radius**2 * height
        # The intersection volume is complex to compute analytically for two offset circles
        # Instead, verify volume is between single cylinder and two full cylinders
        vol = solid.Volume()
        assert vol > single_vol * 0.5, f"Volume too small: {vol:.6f}, single cyl vol = {single_vol:.6f}"
        assert vol <= 2 * single_vol + TOL, f"Volume too large: {vol:.6f}, max = {2*single_vol:.6f}"
    
        # Check we have cylindrical faces (the curved surfaces of the cylinders)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check we have flat top and bottom faces
        top_faces = result.faces(">Z").size()
        bot_faces = result.faces("<Z").size()
        assert top_faces >= 1, f"Expected at least 1 top face, got {top_faces}"
        assert bot_faces >= 1, f"Expected at least 1 bottom face, got {bot_faces}"
    
        # Check the object contains the center points of both cylinders at mid-height
        mid_z = height / 2
        assert solid.isInside((cx1, cy1, mid_z)), f"Solid should contain center of cylinder 1 at ({cx1}, {cy1}, {mid_z})"
        assert solid.isInside((cx2, cy2, mid_z)), f"Solid should contain center of cylinder 2 at ({cx2}, {cy2}, {mid_z})"
    
        # Check the object does NOT contain a point far outside
        assert not solid.isInside((10, 10, mid_z)), "Solid should not contain point (10, 10, mid_z)"
    
        print(f"Volume: {vol:.6f} (single cyl: {single_vol:.6f}, two cyls: {2*single_vol:.6f})")
        print(f"Bounding box: X=[{bb.xmin:.4f}, {bb.xmax:.4f}], Y=[{bb.ymin:.4f}, {bb.ymax:.4f}], Z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Cylindrical faces: {cyl_faces}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00671938/gpt_generated.stl')
