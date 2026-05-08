import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 0.75    # X
        width  = 0.5     # Y
        height = 0.375   # Z
        semi_d = 0.5357  # diameter of semi-circle
        semi_r = semi_d / 2.0  # radius = 0.26785
    
        # --- Step 1: Create the rectangular box ---
        box = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2 & 3: Create semi-circular cutout on the +Y face (longer side) ---
        # The longer sides are the faces with normal in ±Y direction (0.75 long × 0.375 tall)
        # Semi-circle flat edge aligns with the +Y face surface
        # In the workplane on the +Y face:
        #   local X = global X, local Y = global Z
        # Flat edge: horizontal line from (-semi_r, 0) to (semi_r, 0) at face center
        # Arc: goes from (-semi_r, 0) through (0, semi_r) to (semi_r, 0) — upward in local Y (global Z)
        # cutBlind(-width) cuts in -Y direction through the full box width
    
        result = (
            box
            .faces(">Y")
            .workplane()
            .moveTo(-semi_r, 0)
            .lineTo(semi_r, 0)
            .threePointArc((0, semi_r), (-semi_r, 0))
            .close()
            .cutBlind(-width)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Check bounding box — the semi-circle extends beyond the box in Z,
        # so the bounding box should still match the original box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width) < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check:
        # The semi-circle (radius=0.26785) is centered at Z=0 on the face.
        # Box Z range: -0.1875 to +0.1875 (height=0.375).
        # The semi-circle extends from Z=0 to Z=+semi_r=0.26785, but box top is at Z=+0.1875.
        # So the cutout cross-section is a circular segment: the part of the semi-circle
        # within Z in [0, 0.1875] (since semi-circle is the upper half, from Z=0 upward).
        # Wait — the semi-circle flat edge is at Z=0 (face center height), arc goes up to Z=semi_r.
        # The box top is at Z=+0.1875 < semi_r=0.26785, so the arc is clipped.
        #
        # Clipped area = area of circular segment from angle 0 to angle theta,
        # where theta = arccos((semi_r - h_clip) / semi_r) ... 
        # Actually: the circle has center at (0, 0) in local XZ, radius semi_r.
        # The semi-circle is the upper half (Z >= 0). Box clips at Z = height/2 = 0.1875.
        # Clipped area = integral from 0 to h_clip of 2*sqrt(r^2 - z^2) dz
        # where h_clip = min(semi_r, height/2) = 0.1875
        #
        # Area = [z*sqrt(r^2-z^2) + r^2*arcsin(z/r)] from 0 to h_clip
        r = semi_r
        h_clip = min(r, height / 2.0)  # = 0.1875
        # Area of the clipped semi-circle cross-section:
        cutout_area = h_clip * math.sqrt(r**2 - h_clip**2) + r**2 * math.asin(h_clip / r)
        # This is extruded through the full width (Y direction)
        cutout_vol = cutout_area * width
        box_vol = length * width * height
        expected_vol = box_vol - cutout_vol
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that there is a cylindrical face (from the semi-circular cutout)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check that a point inside the semi-circle cutout is NOT inside the solid
        # The cutout is at Y in [-0.25, +0.25], X near 0, Z in [0, ~0.1875]
        # A point at (0, 0, 0.1) should be in the cutout (outside solid)
        solid = result.val()
        point_in_cutout = (0.0, 0.0, 0.1)
        assert not solid.isInside(point_in_cutout), \
            f"Point {point_in_cutout} should be in the cutout (outside solid)"
    
        # A point well inside the solid (away from cutout, at negative Z)
        point_in_solid = (0.3, 0.0, -0.1)
        assert solid.isInside(point_in_solid), \
            f"Point {point_in_solid} should be inside the solid"
    
        # Check face count is more than 6 (original box faces)
        total_faces = result.faces().size()
        assert total_faces > 6, f"Expected more than 6 faces, got {total_faces}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"Total faces: {total_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00995759/gpt_generated.stl')
