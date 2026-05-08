import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        outer_radius = 20.0      # radius of the original circle
        inner_radius = 10.0      # half of outer_radius
        height = 5.0             # small extrusion amount
    
        # --- Step 1: Draw a circle and extrude to create a disk ---
        result = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .extrude(height)
        )
    
        # --- Step 2: Create a circular hole at the center with radius = outer_radius / 2 ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .hole(inner_radius * 2)   # hole() takes diameter
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks: should be 40 x 40 x 5
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 2 * outer_radius) < TOL, \
            f"X length: expected {2 * outer_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * outer_radius) < TOL, \
            f"Y length: expected {2 * outer_radius}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z length: expected {height}, got {bb.zlen}"
    
        # Volume check: annular disk = pi * (R^2 - r^2) * h
        expected_vol = math.pi * (outer_radius**2 - inner_radius**2) * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Cylindrical faces: outer cylinder + inner cylinder = 2
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical faces: expected 2 (outer + inner), got {cyl_face_count}"
    
        # Planar faces: top face + bottom face = 2 (each is an annular ring)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, \
            f"Planar faces: expected 2 (top + bottom annular rings), got {planar_face_count}"
    
        # Total face count: 2 planar + 2 cylindrical = 4
        total_faces = result.faces().size()
        assert total_faces == 4, \
            f"Total faces: expected 4, got {total_faces}"
    
        # Center of mass should be at (0, 0, height/2) by symmetry
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, \
            f"Center of mass Z: expected {height/2}, got {com.z}"
    
        # The center point (0, 0, height/2) should NOT be inside the solid (it's a hole)
        center_inside = result.val().isInside((0, 0, height / 2))
        assert not center_inside, \
            "Center point should be inside the hole, not inside the solid"
    
        # A point on the annular ring should be inside the solid
        mid_radius = (outer_radius + inner_radius) / 2  # 15mm from center
        ring_point = (mid_radius, 0, height / 2)
        ring_inside = result.val().isInside(ring_point)
        assert ring_inside, \
            f"Point at mid-radius {mid_radius}mm should be inside the solid"
    
        # A point outside the outer radius should NOT be inside
        outside_point = (outer_radius + 5, 0, height / 2)
        outside_inside = result.val().isInside(outside_point)
        assert not outside_inside, \
            f"Point outside outer radius should not be inside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670817/gpt_generated.stl')
