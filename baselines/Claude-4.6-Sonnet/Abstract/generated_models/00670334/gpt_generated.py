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
        rect_length = 80.0   # X dimension
        rect_width  = 50.0   # Y dimension
        rect_height = 10.0   # Z dimension (extrusion depth)
        hole_diam   = 15.0   # diameter of the center hole
        hole_radius = hole_diam / 2.0
    
        # --- Step 1: Create a sketch of a rectangle and extrude it ---
        result = (
            cq.Workplane("XY")
            .rect(rect_length, rect_width)   # 2D rectangle sketch centered at origin
            .extrude(rect_height)            # extrude upward in +Z
        )
    
        # --- Step 2: Add a circular through-hole at the center of the rectangle ---
        result = (
            result
            .faces(">Z")          # select the top face
            .workplane()          # set workplane on top face
            .hole(hole_diam)      # drill a through-hole centered at workplane origin (center of rectangle)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - rect_length) < TOL, \
            f"X length: expected {rect_length}, got {bb.xlen}"
        assert abs(bb.ylen - rect_width) < TOL, \
            f"Y length: expected {rect_width}, got {bb.ylen}"
        assert abs(bb.zlen - rect_height) < TOL, \
            f"Z height: expected {rect_height}, got {bb.zlen}"
    
        # 2. Volume check: box volume minus cylinder volume
        box_vol      = rect_length * rect_width * rect_height
        hole_vol     = math.pi * hole_radius**2 * rect_height
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical face check — exactly 1 cylindrical face (the hole wall)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, \
            f"Cylindrical faces: expected 1 (hole wall), got {cyl_faces}"
    
        # 4. Planar face count: top, bottom, 4 sides = 6 planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 6, \
            f"Planar faces: expected 6, got {planar_faces}"
    
        # 5. Total face count: 6 planar + 1 cylindrical = 7
        total_faces = result.faces().size()
        assert total_faces == 7, \
            f"Total faces: expected 7, got {total_faces}"
    
        # 6. Hole passes through center: check that the center point (0,0,5) is NOT inside the solid
        center_point = (0.0, 0.0, rect_height / 2.0)
        is_inside = result.val().isInside(center_point)
        assert not is_inside, \
            f"Center point {center_point} should be inside the hole (not solid), but isInside returned True"
    
        # 7. A point clearly inside the solid (near corner, away from hole) IS inside
        corner_point = (rect_length / 2.0 - 5.0, rect_width / 2.0 - 5.0, rect_height / 2.0)
        assert result.val().isInside(corner_point), \
            f"Corner point {corner_point} should be inside the solid, but isInside returned False"
    
        # 8. Circular edges: top ring + bottom ring of hole = 2 circular edges
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 2, \
            f"Circular edges: expected 2 (top and bottom of hole), got {circ_edges}"
    
        # 9. Center of mass should be at (0, 0, height/2) due to symmetry
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z - rect_height / 2.0) < TOL, \
            f"Center of mass Z: expected {rect_height/2.0}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670334/gpt_generated.stl')
