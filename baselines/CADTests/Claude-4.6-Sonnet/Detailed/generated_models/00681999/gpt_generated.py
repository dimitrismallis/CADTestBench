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
        # --- Step 1: Define the 2D profile as a closed wire ---
        # Rectangle: width=0.75 (X), height=0.5 (Y), centered at origin
        # X: -0.375 to 0.375, Y: -0.25 to 0.25
        # Square cutout: 0.25 x 0.25, top at Y=0.25, bottom at Y=0.0
        # Cutout centered horizontally: X from -0.125 to 0.125
    
        # Draw the profile as a closed polygon (counter-clockwise from bottom-left):
        # Start at bottom-left corner of rectangle
        # Go around the rectangle, but notch out the top-center square
    
        result = (
            cq.Workplane("XY")
            .moveTo(-0.375, -0.25)          # bottom-left of rectangle
            .lineTo(0.375, -0.25)           # bottom-right
            .lineTo(0.375, 0.25)            # top-right
            .lineTo(0.125, 0.25)            # top edge, right side of cutout
            .lineTo(0.125, 0.0)             # right side of cutout, going down
            .lineTo(-0.125, 0.0)            # bottom of cutout
            .lineTo(-0.125, 0.25)           # left side of cutout, going up
            .lineTo(-0.375, 0.25)           # top edge, left side of cutout
            .close()                        # back to bottom-left
            .extrude(0.25)                  # extrude 0.25 units in Z
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 0.75) < TOL, f"X length: expected 0.75, got {bb.xlen}"
        assert abs(bb.ylen - 0.5) < TOL, f"Y length: expected 0.5, got {bb.ylen}"
        assert abs(bb.zlen - 0.25) < TOL, f"Z length (depth): expected 0.25, got {bb.zlen}"
    
        # Volume check:
        # Full rectangle area = 0.75 * 0.5 = 0.375
        # Cutout area = 0.25 * 0.25 = 0.0625
        # Profile area = 0.375 - 0.0625 = 0.3125
        # Volume = 0.3125 * 0.25 = 0.078125
        expected_vol = (0.75 * 0.5 - 0.25 * 0.25) * 0.25
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # Face count check:
        # The extruded shape has:
        # - 1 bottom face (Z=0)
        # - 1 top face (Z=0.25) — but top face has a notch, so it's an L-shape (still 1 face)
        # - Side faces: 8 edges in the profile → 8 rectangular side faces
        # Total = 1 (bottom) + 1 (top) + 8 (sides) = 10 faces
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # Check the cutout exists: a point inside the cutout region should be outside the solid
        solid = result.val()
        # Point inside the cutout (at mid-depth Z=0.125, inside cutout X=0, Y=0.15)
        cutout_point = (0.0, 0.15, 0.125)
        assert not solid.isInside(cutout_point), f"Point {cutout_point} should be outside (in cutout), but is inside"
    
        # Point inside the solid body (bottom half, center)
        inside_point = (0.0, -0.1, 0.125)
        assert solid.isInside(inside_point), f"Point {inside_point} should be inside the solid, but is not"
    
        # Check top face has the notch: faces at max Z should have correct area
        # Top face area = profile area = 0.3125
        top_faces = result.faces(">Z")
        top_face_area = top_faces.val().Area()
        assert abs(top_face_area - 0.3125) < TOL, f"Top face area: expected 0.3125, got {top_face_area}"
    
        # Check bottom face area = same as top face area
        bot_faces = result.faces("<Z")
        bot_face_area = bot_faces.val().Area()
        assert abs(bot_face_area - 0.3125) < TOL, f"Bottom face area: expected 0.3125, got {bot_face_area}"
    
        # Verify the cutout dimensions via facesIntersectedByLine
        # A vertical line through the cutout center (X=0, Y=0.15) going in Z direction
        # should intersect 0 faces (it's in the void)
        faces_through_cutout = solid.facesIntersectedByLine((0.0, 0.15, -1.0), (0, 0, 1))
        assert len(faces_through_cutout) == 0, f"Line through cutout should hit 0 faces, got {len(faces_through_cutout)}"
    
        # A vertical line through the solid body (X=0, Y=-0.1) going in Z direction
        # should intersect 2 faces (top and bottom)
        faces_through_solid = solid.facesIntersectedByLine((0.0, -0.1, -1.0), (0, 0, 1))
        assert len(faces_through_solid) == 2, f"Line through solid body should hit 2 faces, got {len(faces_through_solid)}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00681999/gpt_generated.stl')
