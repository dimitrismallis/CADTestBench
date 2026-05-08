import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        R1 = 20.0    # base cylinder radius
        H1 = 30.0    # base cylinder height
        R2 = 10.0    # top cylinder radius (half of R1)
        H2 = 15.0    # top cylinder height (smaller than H1)
    
        # --- Step 1: Create base cylinder ---
        # Draw a circle of radius R1 on the XY plane and extrude upward by H1
        result = (
            cq.Workplane("XY")
            .circle(R1)
            .extrude(H1)
        )
    
        # --- Step 2: Create smaller cylinder on top ---
        # Select the top face of the base cylinder, place a workplane there,
        # draw a circle of radius R2 (= R1/2) centered at the same point,
        # and extrude upward by H2
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(R2)
            .extrude(H2)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
    
        # Total height should be H1 + H2
        expected_total_height = H1 + H2
        assert abs(bb.zlen - expected_total_height) < TOL, \
            f"Total height: expected {expected_total_height}, got {bb.zlen}"
    
        # Width/depth should be 2*R1 (the base cylinder dominates)
        expected_diameter = 2 * R1
        assert abs(bb.xlen - expected_diameter) < TOL, \
            f"Bounding box X: expected {expected_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - expected_diameter) < TOL, \
            f"Bounding box Y: expected {expected_diameter}, got {bb.ylen}"
    
        # 2. Z extents
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - expected_total_height) < TOL, \
            f"Z max: expected {expected_total_height}, got {bb.zmax}"
    
        # 3. Volume check
        # Volume = pi*R1^2*H1 + pi*R2^2*H2
        vol_base = math.pi * R1**2 * H1
        vol_top  = math.pi * R2**2 * H2
        expected_vol = vol_base + vol_top
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 4. Face count check
        # The tiered cylinder should have:
        #   - 1 bottom flat face (base bottom)
        #   - 1 annular flat face (top of base, minus the top cylinder footprint) — actually a ring face
        #   - 1 top flat face (top of small cylinder)
        #   - 1 cylindrical face for the base cylinder
        #   - 1 cylindrical face for the top cylinder
        # Total = 5 faces
        face_count = result.faces().size()
        assert face_count == 5, \
            f"Face count: expected 5, got {face_count}"
    
        # 5. Cylindrical faces: should be exactly 2 (one per cylinder)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # 6. Planar faces: should be exactly 3 (bottom, annular ring, top)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 3, \
            f"Planar face count: expected 3, got {planar_face_count}"
    
        # 7. Top face center should be at (0, 0, H1+H2)
        top_face_center = result.faces(">Z").val().Center()
        assert abs(top_face_center.x) < TOL, \
            f"Top face center X: expected 0, got {top_face_center.x}"
        assert abs(top_face_center.y) < TOL, \
            f"Top face center Y: expected 0, got {top_face_center.y}"
        assert abs(top_face_center.z - (H1 + H2)) < TOL, \
            f"Top face center Z: expected {H1+H2}, got {top_face_center.z}"
    
        # 8. Bottom face center should be at (0, 0, 0)
        bot_face_center = result.faces("<Z").val().Center()
        assert abs(bot_face_center.x) < TOL, \
            f"Bottom face center X: expected 0, got {bot_face_center.x}"
        assert abs(bot_face_center.y) < TOL, \
            f"Bottom face center Y: expected 0, got {bot_face_center.y}"
        assert abs(bot_face_center.z - 0.0) < TOL, \
            f"Bottom face center Z: expected 0, got {bot_face_center.z}"
    
        # 9. Center of mass should be on the Z axis (x=0, y=0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
    
        # 10. A point inside the base cylinder (but outside top cylinder footprint) should be inside
        test_point_inside = (R1 * 0.8, 0, H1 * 0.5)
        assert result.val().isInside(test_point_inside), \
            f"Point {test_point_inside} should be inside the solid"
    
        # 11. A point outside the base cylinder should NOT be inside
        test_point_outside = (R1 * 1.5, 0, H1 * 0.5)
        assert not result.val().isInside(test_point_outside), \
            f"Point {test_point_outside} should be outside the solid"
    
        # 12. A point in the top cylinder region (within R2) should be inside
        test_point_top = (R2 * 0.5, 0, H1 + H2 * 0.5)
        assert result.val().isInside(test_point_top), \
            f"Point {test_point_top} should be inside the top cylinder"
    
        # 13. A point in the top region but outside R2 should NOT be inside
        test_point_top_outside = (R1 * 0.8, 0, H1 + H2 * 0.5)
        assert not result.val().isInside(test_point_top_outside), \
            f"Point {test_point_top_outside} should be outside the top cylinder"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00995843/gpt_generated.stl')
