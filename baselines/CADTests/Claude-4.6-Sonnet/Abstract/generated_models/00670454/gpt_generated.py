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
        page_width   = 80.0   # X dimension
        page_height  = 110.0  # Y dimension
        page_thick   = 3.0    # Z dimension (small extrusion)
    
        hole_radius  = 4.0    # punch hole radius
        hole_x       = -30.0  # X position of holes (left side)
        hole_y_top   =  35.0  # Y position of top hole
        hole_y_bot   = -35.0  # Y position of bottom hole
    
        # --- Step 1: Create the base rectangular page ---
        result = (
            cq.Workplane("XY")
            .rect(page_width, page_height)
            .extrude(page_thick)
        )
    
        # --- Step 2: Add two punch holes on the left side ---
        # Select the top face, set workplane, then push hole positions
        result = (
            result
            .faces(">Z")
            .workplane()
            .pushPoints([(hole_x, hole_y_top), (hole_x, hole_y_bot)])
            .hole(hole_radius * 2)   # hole() takes diameter
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - page_width)  < TOL, f"X length: expected {page_width}, got {bb.xlen}"
        assert abs(bb.ylen - page_height) < TOL, f"Y length: expected {page_height}, got {bb.ylen}"
        assert abs(bb.zlen - page_thick)  < TOL, f"Z length: expected {page_thick}, got {bb.zlen}"
    
        # Volume check: box minus two cylindrical holes
        box_vol  = page_width * page_height * page_thick
        hole_vol = 2 * math.pi * (hole_radius ** 2) * page_thick
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Two cylindrical faces (one per hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Planar faces: 6 from the box (top, bottom, front, back, left, right).
        # Through-holes do not add extra planar faces — they only cut into the
        # existing top/bottom faces (which remain single planar faces each).
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 6, f"Planar faces: expected 6, got {planar_faces}"
    
        # Holes are on the left side: check that hole centers have negative X
        # The cylindrical faces should have centers with X ≈ hole_x
        cyl_face_list = result.faces("%Cylinder").vals()
        for face in cyl_face_list:
            cx = face.Center().x
            assert cx < 0, f"Hole center X should be negative (left side), got {cx}"
            assert abs(cx - hole_x) < TOL, f"Hole center X: expected {hole_x}, got {cx}"
    
        # Check the two holes are at the correct Y positions
        cyl_centers_y = sorted([f.Center().y for f in cyl_face_list])
        expected_ys   = sorted([hole_y_bot, hole_y_top])
        for cy, ey in zip(cyl_centers_y, expected_ys):
            assert abs(cy - ey) < TOL, f"Hole center Y: expected {ey}, got {cy}"
    
        # Holes should be through the full thickness (Z center at mid-thickness)
        for face in cyl_face_list:
            cz = face.Center().z
            assert abs(cz - page_thick / 2) < TOL, \
                f"Hole center Z: expected {page_thick/2}, got {cz}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670454/gpt_generated.stl')
