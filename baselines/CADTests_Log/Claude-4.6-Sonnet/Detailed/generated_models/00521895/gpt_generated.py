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
        length = 1.0
        width  = 0.75
        height = 0.75
        cyl_diameter = 0.5
        cyl_radius   = cyl_diameter / 2.0  # 0.25
    
        # --- Step 1: Create the rectangular prism (box) centered at origin ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Cut a cylindrical hole through the center of the box ---
        # The hole is centered at (0, 0) on the top face, going through the full height
        result = (
            result
            .faces(">Z")
            .workplane()
            .hole(cyl_diameter)   # cuts a through-hole of given diameter
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check overall bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Check volume: box volume minus cylinder volume
        box_vol = length * width * height
        cyl_vol = math.pi * (cyl_radius ** 2) * height
        expected_vol = box_vol - cyl_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, (
            f"Volume: expected ~{expected_vol:.5f}, got {actual_vol:.5f}"
        )
    
        # Check that there is exactly one cylindrical face (the hole wall)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check that the hole goes all the way through (2 circular edges top and bottom)
        circular_edges = result.edges("%Circle").size()
        assert circular_edges == 2, f"Circular edges: expected 2, got {circular_edges}"
    
        # Check the center of mass is at the origin (symmetric object with centered hole)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected 0, got {com.z}"
    
        # Verify the hole is present by checking a point at the center axis is NOT inside the solid
        center_point = (0.0, 0.0, 0.0)
        assert not result.val().isInside(center_point), (
            "Center point should be inside the hole (not inside solid), but isInside returned True"
        )
    
        # Verify a corner point IS inside the solid
        corner_point = (0.4, 0.3, 0.0)
        assert result.val().isInside(corner_point), (
            f"Corner point {corner_point} should be inside the solid, but isInside returned False"
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00521895/gpt_generated.stl')
