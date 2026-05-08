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
        rect_length = 1.49973      # length of the rectangular portion
        width = 0.16071            # width (diameter of semi-circles)
        radius = width / 2         # = 0.080355
        extrude_h = 0.05357        # extrusion height
        hole_dia = 0.080357        # hole diameter
        hole_radius = hole_dia / 2
    
        # Total length including semi-circular ends
        total_length = rect_length + 2 * radius  # 1.49973 + 0.16071 = 1.66044
    
        # Half dimensions for convenience
        half_len = rect_length / 2   # 0.749865
        half_w = radius              # 0.080355
    
        # --- Step 1: Build stadium shape manually ---
        # Draw the outline: rectangle with semi-circular ends
        # Starting from bottom-left corner of the rectangle, going clockwise:
        # Bottom edge (left to right), right semi-circle, top edge (right to left), left semi-circle
        result = (
            cq.Workplane("XY")
            .moveTo(-half_len, -half_w)
            .lineTo(half_len, -half_w)
            .threePointArc((half_len + radius, 0), (half_len, half_w))
            .lineTo(-half_len, half_w)
            .threePointArc((-half_len - radius, 0), (-half_len, -half_w))
            .close()
            .extrude(extrude_h)
        )
    
        # --- Step 2: Create two holes near the center of each semi-circular end ---
        # Centers of semi-circular ends are at x = ±half_len, y = 0
        result = (
            result
            .faces(">Z")
            .workplane()
            .pushPoints([(half_len, 0), (-half_len, 0)])
            .hole(hole_dia)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        expected_total_length = total_length  # 1.66044
        expected_width = width                # 0.16071
        expected_height = extrude_h           # 0.05357
    
        assert abs(bb.xlen - expected_total_length) < TOL, \
            f"X length: expected {expected_total_length:.5f}, got {bb.xlen:.5f}"
        assert abs(bb.ylen - expected_width) < TOL, \
            f"Y width: expected {expected_width:.5f}, got {bb.ylen:.5f}"
        assert abs(bb.zlen - expected_height) < TOL, \
            f"Z height: expected {expected_height:.5f}, got {bb.zlen:.5f}"
    
        # Check cylindrical faces count (2 semi-circular ends + 2 holes >= 4)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 4, f"Cylindrical faces: expected >= 4, got {cyl_faces}"
    
        # Volume check:
        # Stadium area = rect_length * width + pi * radius^2
        stadium_area = rect_length * width + math.pi * radius**2
        hole_area = 2 * math.pi * hole_radius**2
        expected_vol = (stadium_area - hole_area) * extrude_h
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check holes exist by verifying circular edges on top face
        # Top face should have: 2 outer semi-circle arcs + 2 hole circles = at least 4 circular edges
        top_circular_edges = result.faces(">Z").edges("%Circle").size()
        assert top_circular_edges >= 4, \
            f"Top circular edges: expected >= 4 (2 outer arcs + 2 holes), got {top_circular_edges}"
    
        # Check center of mass is near origin (symmetric shape)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x:.5f}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y:.5f}"
        assert abs(com.z - extrude_h / 2) < TOL, \
            f"Center of mass Z: expected {extrude_h/2:.5f}, got {com.z:.5f}"
    
        # Verify holes by checking that a point inside a hole is NOT inside the solid
        # A point at the center of hole 1, mid-height, should be outside the solid
        solid = result.val()
        hole_center_inside = solid.isInside((half_len, 0, extrude_h / 2))
        assert not hole_center_inside, \
            f"Point at hole center should be outside solid (hole should exist)"
    
        # Verify solid material exists between the holes (center of plate should be inside)
        center_inside = solid.isInside((0, 0, extrude_h / 2))
        assert center_inside, \
            f"Point at plate center should be inside solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00032961/gpt_generated.stl')
