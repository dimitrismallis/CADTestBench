import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 1.5          # X dimension
        width  = 0.016304     # Y dimension
        height = 1.22283      # Z dimension
    
        hole_diameter = 0.130435
        hole_radius   = hole_diameter / 2.0
    
        hole_spacing  = 0.195652   # center-to-center spacing along Z
        first_hole_x_from_left = 0.433378  # distance from left edge (min X) to first hole center
    
        # --- Step 1: Create base rectangular box centered at origin ---
        # Box centered: X in [-0.75, 0.75], Y in [-width/2, width/2], Z in [-height/2, height/2]
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Compute hole positions ---
        # Left edge of box is at X = -length/2 = -0.75
        # First hole X center:
        hole_x = -length / 2.0 + first_hole_x_from_left  # = -0.75 + 0.433378 = -0.316622
    
        # Holes are "aligned along the height" → spaced in Z
        # Place 3 holes centered vertically (symmetric about Z=0)
        hole_z_positions = [
            -hole_spacing,
            0.0,
            hole_spacing
        ]
    
        # --- Step 3: Cut three cylindrical holes through the width (Y direction) ---
        # Use XZ workplane, extrude in both Y directions to ensure full cut through width
        # Note: hole diameter (0.130435) >> box width (0.016304), so each hole produces
        # 2 cylindrical face patches (front and back arcs within the thin slab) = 6 total
        for z_pos in hole_z_positions:
            cyl = (
                cq.Workplane("XZ")
                .center(hole_x, z_pos)
                .circle(hole_radius)
                .extrude(width * 10, both=True)  # extrude well beyond width in both Y directions
            )
            result = result.cut(cyl)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check: box minus 3 cylinders through width
        # Each cylinder passes fully through the width (Y direction)
        box_vol  = length * width * height
        cyl_vol  = math.pi * hole_radius**2 * width
        expected_vol = box_vol - 3 * cyl_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces: 3 holes, each producing 2 cylindrical face patches
        # (because hole diameter >> box width, giving front and back arc surfaces per hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 6, f"Cylindrical faces: expected 6, got {cyl_faces}"
    
        # Check hole positions: points at hole centers should NOT be inside solid
        solid = result.val()
        for z_pos in hole_z_positions:
            hole_center = (hole_x, 0.0, z_pos)
            assert not solid.isInside(hole_center, tolerance=1e-5), \
                f"Point {hole_center} should be inside hole (not solid), but isInside returned True"
    
        # Check that a point in the solid body (away from holes) IS inside
        solid_point = (0.3, 0.0, 0.0)  # far from holes in X
        assert solid.isInside(solid_point, tolerance=1e-5), \
            f"Point {solid_point} should be inside solid, but isInside returned False"
    
        # Check hole X position: verify point at center X (no hole there) is inside solid
        center_point = (0.0, 0.0, 0.0)  # center of box, not at hole X
        assert solid.isInside(center_point, tolerance=1e-5), \
            f"Point {center_point} should be inside solid (no hole here), but isInside returned False"
    
        # Verify holes are through the width: line along Y through each hole center
        # should intersect 0 faces of the solid (open tunnel)
        for z_pos in hole_z_positions:
            faces_hit = solid.facesIntersectedByLine(
                (hole_x, -width * 2, z_pos), (0, 1, 0), direction="AlongAxis"
            )
            # The line passes through the hole, so it should not hit any solid face
            # (the hole is open all the way through)
            assert len(faces_hit) == 0, \
                f"Line through hole at z={z_pos} should hit 0 faces, got {len(faces_hit)}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997373/gpt_generated.stl')
