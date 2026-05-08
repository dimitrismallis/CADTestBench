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
        rect_width = 0.75       # X dimension of rectangle
        rect_height = 0.75      # Y dimension of rectangle
        semi_radius = 0.75 / 2  # = 0.375, semicircle radius
        extrude_h = 0.16071     # extrusion height
        hole_dia = 0.267857     # hole diameter
        hole_radius = hole_dia / 2
    
        # --- Step 1: Build the U-shaped profile ---
        # Rectangle: Y from 0 to 0.75, X from -0.375 to 0.375
        # Semicircle: center at (0, 0), radius 0.375, lower half (Y <= 0)
        #
        # Outline (CCW when viewed from +Z):
        #   Start at (-0.375, 0)
        #   Line up to (-0.375, 0.75)
        #   Line right to (0.375, 0.75)
        #   Line down to (0.375, 0)
        #   Semicircle arc from (0.375, 0) through (0, -0.375) to (-0.375, 0)
        #   Close
    
        result = (
            cq.Workplane("XY")
            .moveTo(-semi_radius, 0)
            .lineTo(-semi_radius, rect_height)
            .lineTo(semi_radius, rect_height)
            .lineTo(semi_radius, 0)
            .threePointArc((0, -semi_radius), (-semi_radius, 0))
            .close()
            .extrude(extrude_h)
        )
    
        # --- Step 2: Circular cutout at center of semicircle ---
        # The semicircle center is at world (0, 0, z).
        # After faces(">Z").workplane(), origin projects to (0, 0, extrude_h).
        # moveTo(0, 0) keeps us at workplane origin = world (0, 0).
        result = (
            result
            .faces(">Z")
            .workplane()
            .moveTo(0, 0)
            .hole(hole_dia, extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - rect_width) < TOL, \
            f"X extent: expected {rect_width}, got {bb.xlen}"
        assert abs(bb.ylen - (rect_height + semi_radius)) < TOL, \
            f"Y extent: expected {rect_height + semi_radius}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_h) < TOL, \
            f"Z extent: expected {extrude_h}, got {bb.zlen}"
    
        # Z bounds
        assert abs(bb.zmin - 0) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_h) < TOL, f"Z max: expected {extrude_h}, got {bb.zmax}"
    
        # Volume check:
        # U-shape area = rectangle area + semicircle area - hole area
        rect_area = rect_width * rect_height
        semi_area = math.pi * semi_radius**2 / 2
        hole_area = math.pi * hole_radius**2
        u_area = rect_area + semi_area
        expected_vol = (u_area - hole_area) * extrude_h
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.5f}, got {actual_vol:.5f}"
    
        # Check cylindrical faces (hole wall + outer curved face of semicircle)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces (semicircle + hole), got {cyl_faces}"
    
        # Check the hole exists: a point at center of semicircle (0,0) at mid-height
        # should be OUTSIDE the solid (it's in the hole void)
        hole_center_inside = solid.isInside((0, 0, extrude_h / 2))
        assert not hole_center_inside, \
            "Hole center (0,0,mid-height) should be outside the solid (inside the hole)"
    
        # Check a point in the rectangle body is inside the solid
        rect_center_inside = solid.isInside((0, rect_height / 2, extrude_h / 2))
        assert rect_center_inside, \
            "Rectangle center should be inside the solid"
    
        # Check a point in the semicircle body (between hole edge and semicircle edge)
        # is inside the solid
        check_r = (hole_radius + semi_radius) / 2  # midpoint between hole edge and semi edge
        semi_body_inside = solid.isInside((check_r, 0, extrude_h / 2))
        assert semi_body_inside, \
            f"Semicircle body at r={check_r:.4f} from center should be inside the solid"
    
        # Check hole goes through: point just inside hole radius at mid-height is void
        small_r = hole_radius * 0.3  # well inside the hole
        inside_hole = solid.isInside((small_r, 0, extrude_h / 2))
        assert not inside_hole, \
            f"Point at r={small_r:.4f} (inside hole) should be outside the solid"
    
        # Verify hole by shooting a line through the solid material (not through the void).
        # A vertical line through a point in the semicircle body (between hole and edge)
        # should intersect the top and bottom faces of the solid.
        faces_hit = solid.facesIntersectedByLine(
            (check_r, 0, -1.0),   # start point below solid, in solid material region
            (0, 0, 1),             # direction upward
            direction="AlongAxis"
        )
        assert len(faces_hit) >= 2, \
            f"Vertical line through solid material should intersect >=2 faces, got {len(faces_hit)}"
    
        # Verify the hole diameter indirectly: the hole radius is hole_radius.
        # A point just outside the hole (at hole_radius * 1.1) should be inside solid.
        just_outside_hole = solid.isInside((hole_radius * 1.1, 0, extrude_h / 2))
        assert just_outside_hole, \
            f"Point just outside hole edge (r={hole_radius*1.1:.4f}) should be inside solid"
    
        # A point just inside the hole (at hole_radius * 0.9) should be outside solid.
        just_inside_hole = solid.isInside((hole_radius * 0.9, 0, extrude_h / 2))
        assert not just_inside_hole, \
            f"Point just inside hole edge (r={hole_radius*0.9:.4f}) should be outside solid"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.5f}, Y={bb.ylen:.5f}, Z={bb.zlen:.5f}")
        print(f"Volume: {actual_vol:.5f} (expected {expected_vol:.5f})")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"Faces hit by vertical line through solid material: {len(faces_hit)}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00031303/gpt_generated.stl')
