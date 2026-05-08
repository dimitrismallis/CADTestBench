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
        height = 0.01463
        outer_diameter = 1.5
        inner_diameter = 1.45232
        outer_radius = outer_diameter / 2.0   # 0.75
        inner_radius = inner_diameter / 2.0   # 0.72616
    
        # --- Step 1: Create outer cylinder ---
        ring = cq.Workplane("XY").cylinder(height, outer_radius)
    
        # --- Step 2: Subtract inner cylinder to create the ring hole ---
        ring = ring.faces(">Z").workplane().circle(inner_radius).cutThruAll()
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = ring.val().BoundingBox()
        assert abs(bb.xlen - outer_diameter) < TOL, \
            f"X bounding box: expected {outer_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - outer_diameter) < TOL, \
            f"Y bounding box: expected {outer_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z bounding box (height): expected {height}, got {bb.zlen}"
    
        # Volume check
        expected_volume = math.pi * (outer_radius**2 - inner_radius**2) * height
        actual_volume = ring.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.01, \
            f"Volume: expected ~{expected_volume:.6f}, got {actual_volume:.6f}"
    
        # Face count: ring should have 4 faces:
        # - top flat annular face
        # - bottom flat annular face
        # - outer cylindrical face
        # - inner cylindrical face
        face_count = ring.faces().size()
        assert face_count == 4, \
            f"Face count: expected 4, got {face_count}"
    
        # Cylindrical faces: should be 2 (outer and inner)
        cyl_face_count = ring.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Planar faces: should be 2 (top and bottom)
        planar_face_count = ring.faces("%Plane").size()
        assert planar_face_count == 2, \
            f"Planar face count: expected 2, got {planar_face_count}"
    
        # Check center of mass is at origin (symmetric ring)
        center = cq.Shape.centerOfMass(ring.val())
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # Check that a point inside the hole is NOT inside the solid
        hole_point = (0.0, 0.0, 0.0)  # center of the ring (inside the hole)
        assert not ring.val().isInside(hole_point), \
            f"Point at center should be inside the hole, not the solid"
    
        # Check that a point in the ring material IS inside the solid
        mid_radius = (outer_radius + inner_radius) / 2.0
        material_point = (mid_radius, 0.0, 0.0)
        assert ring.val().isInside(material_point), \
            f"Point at mid-radius {mid_radius} should be inside the ring material"
    
        return ring
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00005358/gpt_generated.stl')
