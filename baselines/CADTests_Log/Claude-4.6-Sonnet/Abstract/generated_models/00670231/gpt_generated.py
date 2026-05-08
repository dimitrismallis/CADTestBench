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
        rect_width  = 40.0   # Y dimension
        rect_height = 10.0   # Z (extrusion height)
        hole_diam   = 10.0   # diameter of the circular hole
        hole_radius = hole_diam / 2.0
    
        # Hole offset: slightly to the left (negative X) of center
        # Rectangle center is at (0, 0); shift hole left by 10mm
        hole_offset_x = -10.0   # left of center
        hole_offset_y =   0.0   # centered in Y
    
        # --- Step 1: Create and extrude the rectangle ---
        result = (
            cq.Workplane("XY")
            .rect(rect_length, rect_width)
            .extrude(rect_height)
        )
    
        # --- Step 2: Add a circular hole offset to the left of center ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .center(hole_offset_x, hole_offset_y)
            .hole(hole_diam)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - rect_length) < TOL, \
            f"X length: expected {rect_length}, got {bb.xlen}"
        assert abs(bb.ylen - rect_width) < TOL, \
            f"Y length: expected {rect_width}, got {bb.ylen}"
        assert abs(bb.zlen - rect_height) < TOL, \
            f"Z height: expected {rect_height}, got {bb.zlen}"
    
        # 2. Volume check: box minus cylinder
        box_vol  = rect_length * rect_width * rect_height
        hole_vol = math.pi * hole_radius**2 * rect_height
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical face check: exactly 1 cylindrical face (the hole wall)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, \
            f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # 4. Verify the hole is to the LEFT of the rectangle center
        #    The hole center in X should be at hole_offset_x (negative = left)
        #    We check by probing: a point at (hole_offset_x, 0, 5) should be OUTSIDE
        #    (inside the hole), and a point at (+10, 0, 5) should be INSIDE the solid.
        shape = result.val()
    
        # Point inside the hole (should be outside the solid)
        point_in_hole = (hole_offset_x, 0.0, rect_height / 2.0)
        assert not shape.isInside(point_in_hole), \
            f"Point {point_in_hole} should be outside solid (inside hole), but isInside returned True"
    
        # Point at the right side of center (no hole there, should be inside solid)
        point_right_of_center = (10.0, 0.0, rect_height / 2.0)
        assert shape.isInside(point_right_of_center), \
            f"Point {point_right_of_center} should be inside solid, but isInside returned False"
    
        # 5. Verify hole is closer to left edge than right edge
        #    Left edge X = -rect_length/2 = -40; right edge X = +40
        #    Distance from hole center to left edge:  hole_offset_x - (-40) = 30
        #    Distance from hole center to right edge: 40 - hole_offset_x    = 50
        dist_to_left  = hole_offset_x - (-rect_length / 2.0)
        dist_to_right = (rect_length / 2.0) - hole_offset_x
        assert dist_to_left < dist_to_right, \
            f"Hole should be closer to left edge: dist_left={dist_to_left}, dist_right={dist_to_right}"
    
        # 6. Face count:
        #    A box has 6 faces. Adding a through-hole:
        #    - Top and bottom faces become annular rings (still 2 planar faces)
        #    - 1 cylindrical face added (hole wall)
        #    Total = 4 side faces + 2 annular faces + 1 cylindrical = 7 faces
        total_faces = result.faces().size()
        assert total_faces == 7, \
            f"Total faces: expected 7, got {total_faces}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen} x {bb.ylen} x {bb.zlen}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Total faces: {total_faces}")
        print(f"  Hole offset X: {hole_offset_x} (left of center)")
        print(f"  Dist to left edge: {dist_to_left}, dist to right edge: {dist_to_right}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670231/gpt_generated.stl')
