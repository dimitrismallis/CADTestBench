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
        main_w = 60.0    # main rectangle width (X)
        main_h = 40.0    # main rectangle height (Y)
        tab_w  = 20.0    # tab width (X)
        tab_h  = 15.0    # tab height (Y)
        thickness = 10.0 # extrusion height (Z)
        hole_d = 20.0    # central hole diameter
    
        # --- Step 1: Build the combined 2D profile using Sketch API ---
        # Main rectangle centered at origin
        # Two tabs: one on top (center of top long edge), one on bottom (center of bottom long edge)
        # Top tab: centered at (0, main_h/2 + tab_h/2)
        # Bottom tab: centered at (0, -main_h/2 - tab_h/2)
    
        s = (
            cq.Sketch()
            # Main rectangle
            .rect(main_w, main_h)
            # Top tab (attached to center of top long edge)
            .push([(0, main_h / 2 + tab_h / 2)])
            .rect(tab_w, tab_h)
            # Bottom tab (attached to center of bottom long edge)
            .push([(0, -(main_h / 2 + tab_h / 2))])
            .rect(tab_w, tab_h)
        )
    
        # --- Step 2: Extrude the sketch ---
        result = cq.Workplane("XY").placeSketch(s).extrude(thickness)
    
        # --- Step 3: Create a large circular hole at the center ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .hole(hole_d)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        expected_xlen = main_w
        expected_ylen = main_h + 2 * tab_h   # main + two tabs
        expected_zlen = thickness
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check
        # Total solid volume = main_rect + 2 tabs - hole
        solid_vol = (main_w * main_h * thickness) + 2 * (tab_w * tab_h * thickness)
        hole_vol  = math.pi * (hole_d / 2) ** 2 * thickness
        expected_vol = solid_vol - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check cylindrical face exists (the hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Expected at least 1 cylindrical face (hole), got {cyl_faces}"
    
        # Check the hole goes through: a point at center should be outside the solid
        center_point = (0, 0, thickness / 2)
        solid_shape = result.val()
        assert not solid_shape.isInside(center_point), \
            "Center point should be inside the hole (outside solid), but isInside returned True"
    
        # Check that a point in the main body (offset from center) is inside
        body_point = (main_w / 4, 0, thickness / 2)
        assert solid_shape.isInside(body_point), \
            f"Point {body_point} should be inside the main body"
    
        # Check that a point in the top tab is inside
        top_tab_point = (0, main_h / 2 + tab_h / 2, thickness / 2)
        assert solid_shape.isInside(top_tab_point), \
            f"Point {top_tab_point} should be inside the top tab"
    
        # Check that a point in the bottom tab is inside
        bot_tab_point = (0, -(main_h / 2 + tab_h / 2), thickness / 2)
        assert solid_shape.isInside(bot_tab_point), \
            f"Point {bot_tab_point} should be inside the bottom tab"
    
        # Check that a point outside the shape is not inside
        outside_point = (main_w, main_h, thickness / 2)
        assert not solid_shape.isInside(outside_point), \
            f"Point {outside_point} should be outside the solid"
    
        # Check planar faces count: top + bottom + sides of main rect + sides of tabs + hole rings
        # At minimum we expect more than 6 faces (a plain box has 6)
        total_faces = result.faces().size()
        assert total_faces > 6, \
            f"Expected more than 6 faces for puzzle piece shape, got {total_faces}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} (expected ~{expected_vol:.2f})")
        print(f"Total faces: {total_faces}, Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997071/gpt_generated.stl')
