import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        R_outer = 20.0       # outer radius
        R_inner = 16.0       # inner radius (slightly smaller, 4mm wall)
        angle_deg = 60.0     # sector angle in degrees
        height = 10.0        # extrusion height
    
        angle_rad = math.radians(angle_deg)
    
        # Key points on the annular sector profile
        outer_start = (R_outer, 0.0)
        outer_end   = (R_outer * math.cos(angle_rad), R_outer * math.sin(angle_rad))
        inner_start = (R_inner, 0.0)
        inner_end   = (R_inner * math.cos(angle_rad), R_inner * math.sin(angle_rad))
    
        # --- Step 1: Sketch the outer minor sector (60°, radius=20) and extrude ---
        # This creates the solid "pie slice" shape
        outer_sector = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(outer_start[0], outer_start[1])
            .radiusArc(outer_end, R_outer)
            .lineTo(0, 0)
            .close()
            .extrude(height)
        )
    
        # --- Step 2: Sketch the inner sector (same angle, radius=16) ---
        # Place it on the XY plane (same base), extrude same height, then subtract
        # This hollows out the inside leaving a hollow-cylinder sector
        inner_sector = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(inner_start[0], inner_start[1])
            .radiusArc(inner_end, R_inner)
            .lineTo(0, 0)
            .close()
            .extrude(height)
        )
    
        # --- Step 3: Cut inner sector from outer sector ---
        result = outer_sector.cut(inner_sector)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Explicitly get the solid for geometry checks
        solid = result.solids().val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        # X: from 0 to R_outer=20
        assert abs(bb.xmin) < TOL, f"xmin expected ~0, got {bb.xmin}"
        assert abs(bb.xmax - R_outer) < TOL, f"xmax expected ~{R_outer}, got {bb.xmax}"
    
        # Y: from 0 to R_outer * sin(60°) ≈ 17.32
        expected_ymax = R_outer * math.sin(angle_rad)
        assert abs(bb.ymin) < TOL, f"ymin expected ~0, got {bb.ymin}"
        assert abs(bb.ymax - expected_ymax) < TOL, \
            f"ymax expected ~{expected_ymax:.3f}, got {bb.ymax:.3f}"
    
        # Z: 0 to height=10
        assert abs(bb.zmin) < TOL, f"zmin expected ~0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"zmax expected ~{height}, got {bb.zmax}"
    
        # Volume: annular sector = 0.5 * angle_rad * (R_outer^2 - R_inner^2) * height
        expected_vol = 0.5 * angle_rad * (R_outer**2 - R_inner**2) * height
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Exactly 1 solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # 2 cylindrical faces: outer arc wall and inner arc wall
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Expected 2 cylindrical faces (inner + outer arc), got {cyl_faces}"
    
        # 4 planar faces: bottom, top, two flat radial sides
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 4, \
            f"Expected 4 planar faces, got {planar_faces}"
    
        # Total faces = 6
        total_faces = result.faces().size()
        assert total_faces == 6, \
            f"Expected 6 total faces, got {total_faces}"
    
        # Hollowness: point at radius < R_inner should NOT be inside solid
        inner_test_pt = (
            8.0 * math.cos(math.radians(30)),
            8.0 * math.sin(math.radians(30)),
            5.0
        )
        assert not solid.isInside(inner_test_pt), \
            f"Point inside inner radius should NOT be inside solid: {inner_test_pt}"
    
        # Point in the wall (R_inner < r < R_outer) should be inside
        mid_r = (R_inner + R_outer) / 2.0  # 18mm
        wall_test_pt = (
            mid_r * math.cos(math.radians(30)),
            mid_r * math.sin(math.radians(30)),
            5.0
        )
        assert solid.isInside(wall_test_pt), \
            f"Point in wall should be inside solid: {wall_test_pt}"
    
        # Point outside outer radius should NOT be inside
        outer_test_pt = (
            25.0 * math.cos(math.radians(30)),
            25.0 * math.sin(math.radians(30)),
            5.0
        )
        assert not solid.isInside(outer_test_pt), \
            f"Point outside outer radius should NOT be inside solid: {outer_test_pt}"
    
        print("All assertions passed!")
        print(f"Volume: {actual_vol:.3f} mm³ (expected {expected_vol:.3f} mm³)")
        print(f"Bounding box: x=[{bb.xmin:.2f},{bb.xmax:.2f}], "
              f"y=[{bb.ymin:.2f},{bb.ymax:.2f}], z=[{bb.zmin:.2f},{bb.zmax:.2f}]")
        print(f"Cylindrical faces: {cyl_faces}, Planar faces: {planar_faces}, "
              f"Total: {total_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00684841/gpt_generated.stl')
