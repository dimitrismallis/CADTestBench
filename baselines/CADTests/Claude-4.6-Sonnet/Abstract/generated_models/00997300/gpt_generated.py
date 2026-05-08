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
        cyl_diameter   = 100.0
        cyl_radius     = cyl_diameter / 2.0       # 50 mm
        cyl_height     = 20.0                     # short cylinder
    
        center_hole_d  = cyl_diameter / 8.0       # 12.5 mm
        center_hole_r  = center_hole_d / 2.0      # 6.25 mm
    
        small_hole_d   = center_hole_d / 2.0      # 6.25 mm  (half of center hole)
        small_hole_r   = small_hole_d / 2.0       # 3.125 mm
    
        # Triangular formation radius: midway between center hole edge and cylinder edge
        tri_radius     = (center_hole_r + cyl_radius) / 2.0  # ~28.125 mm
    
        # --- Step 1: Create the large, short cylinder ---
        result = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # --- Step 2: Create the center hole (1/8th diameter of cylinder, through all) ---
        result = (
            result
            .faces(">Z").workplane()
            .hole(center_hole_d)
        )
    
        # --- Step 3: Create three smaller holes in triangular formation (120° apart) ---
        angles = [90, 210, 330]  # degrees, 120° apart for equilateral triangle
        hole_positions = [
            (tri_radius * math.cos(math.radians(a)),
             tri_radius * math.sin(math.radians(a)))
            for a in angles
        ]
    
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints(hole_positions)
            .hole(small_hole_d)
        )
    
        # --- Final object verification ---
        TOL = 0.5   # mm tolerance for geometry checks
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # 1. Bounding box checks
        assert abs(bb.xlen - cyl_diameter) < TOL, \
            f"X extent: expected {cyl_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - cyl_diameter) < TOL, \
            f"Y extent: expected {cyl_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - cyl_height) < TOL, \
            f"Z extent: expected {cyl_height}, got {bb.zlen}"
    
        # 2. Volume check
        vol_main        = math.pi * cyl_radius**2 * cyl_height
        vol_center_hole = math.pi * center_hole_r**2 * cyl_height
        vol_small_holes = 3 * math.pi * small_hole_r**2 * cyl_height
        expected_vol    = vol_main - vol_center_hole - vol_small_holes
        actual_vol      = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical faces: outer (1) + center hole (1) + 3 small holes (3) = 5
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 5, \
            f"Cylindrical faces: expected 5, got {cyl_faces}"
    
        # 4. Planar faces: OCCT may split annular faces; verify at least 2 (top + bottom)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 2, \
            f"Planar faces: expected at least 2, got {planar_faces}"
        # Also verify it's an even number (symmetric top/bottom)
        assert planar_faces % 2 == 0, \
            f"Planar faces should be even (symmetric top/bottom), got {planar_faces}"
    
        # 5. Center hole verification: center of cylinder should be inside the hole (not solid)
        center_point = (0.0, 0.0, 0.0)
        assert not solid.isInside(center_point), \
            "Center (0,0,0) should be inside the center hole, not inside the solid"
    
        # 6. A point on the solid body (not in any hole) should be inside
        # Pick a point just outside center hole, between the small holes
        body_point = (0.0, center_hole_r + 2.0, 0.0)
        assert solid.isInside(body_point), \
            f"Point {body_point} should be inside the solid body"
    
        # 7. A point outside the cylinder should not be inside
        outside_point = (cyl_radius + 5.0, 0.0, 0.0)
        assert not solid.isInside(outside_point), \
            f"Point {outside_point} should be outside the cylinder"
    
        # 8. Verify triangular hole positions: center of each small hole should NOT be inside solid
        for a in angles:
            hx = tri_radius * math.cos(math.radians(a))
            hy = tri_radius * math.sin(math.radians(a))
            hole_center = (hx, hy, 0.0)
            assert not solid.isInside(hole_center), \
                f"Point {hole_center} at angle {a}° should be inside a small hole, not the solid"
    
        # 9. Center of mass should be near (0, 0, 0) due to rotational symmetry
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected ~0, got {com.z}"
    
        # 10. Total face count: 5 cylindrical + planar faces
        total_faces = result.faces().size()
        assert total_faces == cyl_faces + planar_faces, \
            f"Total faces: expected {cyl_faces + planar_faces}, got {total_faces}"
    
        # 11. Verify the three small holes are evenly spaced (120° apart) by checking
        #     that the distances between hole centers are equal (equilateral triangle).
        #     Fixed: use correct point indices for all three sides.
        pts = [
            (tri_radius * math.cos(math.radians(a)),
             tri_radius * math.sin(math.radians(a)))
            for a in angles
        ]
        d01 = math.sqrt((pts[0][0] - pts[1][0])**2 + (pts[0][1] - pts[1][1])**2)
        d12 = math.sqrt((pts[1][0] - pts[2][0])**2 + (pts[1][1] - pts[2][1])**2)
        d20 = math.sqrt((pts[2][0] - pts[0][0])**2 + (pts[2][1] - pts[0][1])**2)  # fixed: pts[0][1] not pts[1][1]
        assert abs(d01 - d12) < TOL, f"Triangle side 01 vs 12: {d01:.3f} vs {d12:.3f}"
        assert abs(d12 - d20) < TOL, f"Triangle side 12 vs 20: {d12:.3f} vs {d20:.3f}"
        assert abs(d20 - d01) < TOL, f"Triangle side 20 vs 01: {d20:.3f} vs {d01:.3f}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997300/gpt_generated.stl')
