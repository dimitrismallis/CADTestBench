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
        length      = 100.0   # long dimension (X)
        width       = 40.0    # short dimension (Y)
        height      = 5.0     # small extrusion height (Z)
        hole_diam   = 6.0     # diameter of each hole
        hole_radius = hole_diam / 2.0
    
        # Triangle formation centres (relative to plate centre at origin):
        #   Top hole:          (0,  +12)
        #   Bottom-left hole:  (-15, -12)
        #   Bottom-right hole: (+15, -12)
        hole_positions = [
            (0.0,   12.0),
            (-15.0, -12.0),
            ( 15.0, -12.0),
        ]
    
        # --- Step 1: Create the long rectangular base plate ---
        # box() is centered by default: spans X[-50,50], Y[-20,20], Z[-2.5,2.5]
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Drill three through-holes in a triangular formation ---
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints(hole_positions)
            .hole(hole_diam)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 2a. Bounding box — plate dimensions unchanged by through-holes
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y length: expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # 2b. Volume: box minus three cylindrical holes
        box_vol      = length * width * height
        hole_vol_one = math.pi * hole_radius**2 * height
        hole_vol     = 3 * hole_vol_one
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, (
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
        )
    
        # 2c. Exactly 3 cylindrical faces (one per hole)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 3, (
            f"Cylindrical faces: expected 3 (one per hole), got {cyl_face_count}"
        )
    
        # 2d. Exactly 3 circular edges on the top face (hole openings)
        top_circle_count = result.faces(">Z").edges("%Circle").size()
        assert top_circle_count == 3, (
            f"Circular edges on top face: expected 3, got {top_circle_count}"
        )
    
        # 2e. Exactly 3 circular edges on the bottom face (hole exits)
        bot_circle_count = result.faces("<Z").edges("%Circle").size()
        assert bot_circle_count == 3, (
            f"Circular edges on bottom face: expected 3, got {bot_circle_count}"
        )
    
        # 2f. Verify holes go all the way through — points inside holes are NOT in solid
        solid = result.val()
        for (hx, hy) in hole_positions:
            # box is centered, so Z midpoint is 0
            pt = (hx, hy, 0.0)
            assert not solid.isInside(pt), (
                f"Point {pt} should be inside a hole (not solid), but isInside returned True"
            )
    
        # 2g. Centre of mass — compute analytically
        # Box is centered at origin (0, 0, 0).
        # Removing hole material shifts CoM:
        #   CoM_axis = (box_vol * 0 - sum(hole_vol_one * hole_center_axis)) / net_vol
        net_vol = box_vol - hole_vol
    
        # X: holes at x=0, -15, +15 → sum = 0, so CoM X stays at 0
        expected_com_x = (box_vol * 0.0 - sum(hole_vol_one * hx for hx, hy in hole_positions)) / net_vol
        # Y: holes at y=+12, -12, -12 → sum = -12, so CoM Y shifts slightly positive
        expected_com_y = (box_vol * 0.0 - sum(hole_vol_one * hy for hx, hy in hole_positions)) / net_vol
        # Z: box centered at 0, holes symmetric in Z → CoM Z = 0
        expected_com_z = 0.0
    
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x - expected_com_x) < TOL, (
            f"CoM X: expected ~{expected_com_x:.4f}, got {com.x:.4f}"
        )
        assert abs(com.y - expected_com_y) < TOL, (
            f"CoM Y: expected ~{expected_com_y:.4f}, got {com.y:.4f}"
        )
        assert abs(com.z - expected_com_z) < TOL, (
            f"CoM Z: expected {expected_com_z:.4f}, got {com.z:.4f}"
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00996473/gpt_generated.stl')
