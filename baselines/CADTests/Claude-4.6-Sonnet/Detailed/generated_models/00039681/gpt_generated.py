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
        outer_diameter = 1.0
        outer_radius   = outer_diameter / 2.0
    
        hole1_diameter = 0.332143
        hole1_radius   = hole1_diameter / 2.0
        height1        = 0.242143
    
        hole2_diameter = 0.728571
        hole2_radius   = hole2_diameter / 2.0
        height2        = 0.321568
    
        total_height   = height1 + height2  # ~0.563711
    
        # --- Step 1: First pipe section (smaller hole) ---
        # Annular cross-section: outer circle minus inner circle, extruded upward
        part = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .circle(hole1_radius)
            .extrude(height1)
        )
    
        # --- Step 2: Second pipe section (larger hole) stacked on top ---
        # Move to the top face of the first section and extrude the second annulus
        part = (
            part
            .faces(">Z")
            .workplane()
            .circle(outer_radius)
            .circle(hole2_radius)
            .extrude(height2)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = part.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - outer_diameter) < TOL, \
            f"X extent: expected {outer_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - outer_diameter) < TOL, \
            f"Y extent: expected {outer_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - total_height) < TOL, \
            f"Total height: expected {total_height:.6f}, got {bb.zlen:.6f}"
    
        # Volume check
        # Section 1: pi*(R^2 - r1^2)*h1
        vol1 = math.pi * (outer_radius**2 - hole1_radius**2) * height1
        # Section 2: pi*(R^2 - r2^2)*h2
        vol2 = math.pi * (outer_radius**2 - hole2_radius**2) * height2
        expected_vol = vol1 + vol2
        actual_vol = part.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Cylindrical faces: 4 (outer cylinder, inner cylinder section 1, inner cylinder section 2, and the junction)
        # Actually: outer surface (1 or 2 depending on merge), inner1, inner2 = at least 3 cylindrical faces
        cyl_faces = part.faces("%Cylinder").size()
        assert cyl_faces >= 3, \
            f"Expected at least 3 cylindrical faces, got {cyl_faces}"
    
        # Check that the smaller hole is present at z = height1/2 (midpoint of first section)
        # A point at the center of the first hole should be INSIDE the hole (outside the solid)
        mid_z1 = height1 / 2.0
        point_in_hole1 = (0.0, 0.0, mid_z1)
        assert not part.val().isInside(point_in_hole1), \
            f"Point {point_in_hole1} should be inside hole1 (outside solid), but isInside returned True"
    
        # Check that the larger hole is present at z = height1 + height2/2
        mid_z2 = height1 + height2 / 2.0
        point_in_hole2 = (0.0, 0.0, mid_z2)
        assert not part.val().isInside(point_in_hole2), \
            f"Point {point_in_hole2} should be inside hole2 (outside solid), but isInside returned True"
    
        # Check that a point in the wall of section 1 IS inside the solid
        wall_point1 = (outer_radius * 0.8, 0.0, mid_z1)
        assert part.val().isInside(wall_point1), \
            f"Point {wall_point1} should be inside the wall of section 1, but isInside returned False"
    
        # Check that a point in the wall of section 2 IS inside the solid
        wall_point2 = (outer_radius * 0.8, 0.0, mid_z2)
        assert part.val().isInside(wall_point2), \
            f"Point {wall_point2} should be inside the wall of section 2, but isInside returned False"
    
        # Check that a point between hole1 radius and hole2 radius at section2 height is INSIDE the hole
        # (since hole2 is larger, a point at hole1_radius distance from center should be in the hole at section2)
        mid_hole_point = (hole1_radius * 0.5, 0.0, mid_z2)
        assert not part.val().isInside(mid_hole_point), \
            f"Point {mid_hole_point} should be inside hole2 (outside solid), but isInside returned True"
    
        # Verify the annular ring at section1 height: point between hole1 and outer radius should be solid
        ring_point1 = ((hole1_radius + outer_radius) / 2.0, 0.0, mid_z1)
        assert part.val().isInside(ring_point1), \
            f"Point {ring_point1} should be inside wall of section 1, but isInside returned False"
    
        # Verify the annular ring at section2 height: point between hole2 and outer radius should be solid
        ring_point2 = ((hole2_radius + outer_radius) / 2.0, 0.0, mid_z2)
        assert part.val().isInside(ring_point2), \
            f"Point {ring_point2} should be inside wall of section 2, but isInside returned False"
    
        print(f"All assertions passed!")
        print(f"Total height: {bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Cylindrical faces: {cyl_faces}")
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00039681/gpt_generated.stl')
