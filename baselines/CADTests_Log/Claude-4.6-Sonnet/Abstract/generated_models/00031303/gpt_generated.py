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
        rect_width = 40.0       # rectangle width
        rect_height = 60.0      # rectangle height
        semi_radius = rect_width / 2   # = 20, semicircle radius = half of width
        extrude_depth = 10.0    # extrusion thickness
    
        # Hole: diameter = semicircle_diameter / 4 = (2*semi_radius) / 4 = semi_radius / 2
        hole_diameter = (2 * semi_radius) / 4   # = 10
        hole_radius = hole_diameter / 2          # = 5
    
        # --- Step 1: Build the U-shaped (tag) profile ---
        # Rectangle centered at origin: x in [-20,20], y in [-30, 30]
        # Semicircle at bottom: center at (0, -30), radius 20, opening downward
        # We'll draw the profile as a closed wire:
        #   Start at top-left corner (-20, 30)
        #   Go right to (20, 30)
        #   Go down to (20, -30)
        #   Semicircle arc from (20, -30) to (-20, -30) going through (0, -50)
        #   Go up back to (-20, 30)
    
        # The semicircle center is at (0, -30), radius 20
        # Arc midpoint (bottom of semicircle): (0, -30 - 20) = (0, -50)
    
        result = (
            cq.Workplane("XY")
            .moveTo(-rect_width/2, rect_height/2)          # top-left
            .lineTo(rect_width/2, rect_height/2)            # top-right
            .lineTo(rect_width/2, -rect_height/2)           # bottom-right
            .threePointArc(
                (0, -rect_height/2 - semi_radius),          # bottom of arc (0, -50)
                (-rect_width/2, -rect_height/2)             # bottom-left
            )
            .lineTo(-rect_width/2, rect_height/2)           # back to top-left
            .close()
            .extrude(extrude_depth)
        )
    
        # --- Step 2: Circular cutout at the center of the semicircle ---
        # Semicircle center in 2D: (0, -rect_height/2) = (0, -30)
        # This point is on the bottom edge of the rectangle / top of the semicircle
        # The "center of the semicircle" = (0, -30) in XY, at Z = extrude_depth (top face)
    
        result = (
            result
            .faces(">Z")
            .workplane()
            .center(0, -rect_height/2)   # move to semicircle center (0, -30)
            .circle(hole_radius)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        # X: from -20 to 20 → xlen = 40
        assert abs(bb.xlen - rect_width) < TOL, f"X length: expected {rect_width}, got {bb.xlen}"
        # Y: from -50 (bottom of arc) to 30 (top of rect) → ylen = 80
        expected_ylen = rect_height/2 + semi_radius   # 30 + 20 = 50... wait
        # rect top = 30, arc bottom = -50, so ylen = 30 - (-50) = 80
        expected_ylen = rect_height/2 + rect_height/2 + semi_radius  # 30 + 30 + 20 = 80
        assert abs(bb.ylen - expected_ylen) < TOL, f"Y length: expected {expected_ylen}, got {bb.ylen}"
        # Z: extrude_depth = 10
        assert abs(bb.zlen - extrude_depth) < TOL, f"Z length: expected {extrude_depth}, got {bb.zlen}"
    
        # Volume check
        # Area of U-shape = rectangle area + semicircle area - hole area
        rect_area = rect_width * rect_height                    # 40 * 60 = 2400
        semi_area = math.pi * semi_radius**2 / 2               # pi * 400 / 2 = 628.318...
        hole_area = math.pi * hole_radius**2                    # pi * 25 = 78.539...
        expected_vol = (rect_area + semi_area - hole_area) * extrude_depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check cylindrical face exists (the hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face (hole), got {cyl_faces}"
    
        # Check the hole goes through: a point at the hole center should be outside the solid
        # Hole center in 3D: (0, -30, 5) — inside the hole
        solid = result.val()
        hole_center_inside = solid.isInside((0, -rect_height/2, extrude_depth/2))
        assert not hole_center_inside, "Point at hole center should be outside (inside the hole cutout)"
    
        # Check a point clearly inside the body is inside
        body_point = solid.isInside((0, 0, extrude_depth/2))
        assert body_point, "Point at body center should be inside the solid"
    
        # Check the semicircle bottom point is outside (it's on the boundary/surface)
        # A point just inside the arc should be inside
        arc_interior = solid.isInside((0, -rect_height/2 - semi_radius/2, extrude_depth/2))
        assert arc_interior, f"Point inside semicircle region should be inside solid"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00031303/gpt_generated.stl')
