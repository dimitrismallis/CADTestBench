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
        outer_diameter = 1.5
        height = 0.00656
        inner_diameter = outer_diameter - 2 * 0.203459  # = 1.093082
    
        outer_radius = outer_diameter / 2   # 0.75
        inner_radius = inner_diameter / 2   # 0.546541
    
        # --- Step 1: Create the ring profile on the YZ plane ---
        # The ring is extruded along X-axis, so we work on the YZ plane.
        # We create an annulus: outer circle minus inner circle.
        # Extrude symmetrically along X so center is at x=0 (midpoint of height).
    
        ring = (
            cq.Workplane("YZ")
            .circle(outer_radius)
            .circle(inner_radius)
            .extrude(height / 2, both=True)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = ring.val().BoundingBox()
    
        # Bounding box along X should equal height (0.00656)
        assert abs(bb.xlen - height) < TOL, f"X length (height): expected {height}, got {bb.xlen}"
    
        # Bounding box along Y and Z should equal outer diameter (1.5)
        assert abs(bb.ylen - outer_diameter) < TOL, f"Y length (outer dia): expected {outer_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - outer_diameter) < TOL, f"Z length (outer dia): expected {outer_diameter}, got {bb.zlen}"
    
        # Center of ring should be at origin (midpoint of height along X)
        center = ring.val().Center()
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # Volume check: annulus area * height
        annulus_area = math.pi * (outer_radius**2 - inner_radius**2)
        expected_volume = annulus_area * height
        actual_volume = ring.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.01, \
            f"Volume: expected ~{expected_volume:.6f}, got {actual_volume:.6f}"
    
        # Check cylindrical faces: 4 cylindrical faces
        # (outer cylinder split into 2 halves + inner cylinder split into 2 halves)
        cyl_faces = ring.faces("%Cylinder").size()
        assert cyl_faces == 4, f"Cylindrical faces: expected 4, got {cyl_faces}"
    
        # Check planar faces: 2 flat annular end faces
        planar_faces = ring.faces("%Plane").size()
        assert planar_faces == 2, f"Planar faces: expected 2, got {planar_faces}"
    
        # Verify the hole exists: a point at the center of the ring (y=0, z=0)
        # at x=0 (center of hole) should NOT be inside the solid
        solid = ring.val()
        point_in_hole = (0, 0, 0)
        assert not solid.isInside(point_in_hole), \
            f"Point at center (0,0,0) should be in the hole, not inside the solid"
    
        # Check a point at mid-radius is inside the solid
        mid_radius = (outer_radius + inner_radius) / 2
        point_in_ring = (0, mid_radius, 0)
        assert solid.isInside(point_in_ring), \
            f"Point at mid-radius {point_in_ring} should be inside the solid"
    
        return ring
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00680715/gpt_generated.stl')
