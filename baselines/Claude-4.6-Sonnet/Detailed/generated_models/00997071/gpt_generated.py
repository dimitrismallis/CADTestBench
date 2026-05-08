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
        main_len = 0.636792       # X dimension of main rectangle
        main_wid = 0.56638        # Y dimension of main rectangle
        tab_extra = 0.113207      # extra on each side of tab in X
        tab_len = main_len + 2 * tab_extra  # = 0.863206
        tab_wid = 0.141509        # Y dimension of each tab rectangle
        height = 0.099057         # extrusion height
        hole_dia = 0.318396       # hole diameter
        hole_rad = hole_dia / 2   # = 0.159198
    
        # Tab centers in Y: main rect goes from -main_wid/2 to +main_wid/2
        # Tabs connect at the longer edges (top and bottom), extending outward
        tab_y_offset = main_wid / 2 + tab_wid / 2  # center of each tab in Y
    
        # --- Step 1: Build combined 2D profile using Sketch API ---
        # Union of three rectangles: main + top tab + bottom tab
        s = (
            cq.Sketch()
            .rect(main_len, main_wid)
            .reset()
            .push([(0, tab_y_offset)])
            .rect(tab_len, tab_wid)
            .reset()
            .push([(0, -tab_y_offset)])
            .rect(tab_len, tab_wid)
            .reset()
        )
    
        # --- Step 2: Extrude combined shape ---
        result = cq.Workplane("XY").placeSketch(s).extrude(height)
    
        # --- Step 3: Cut circular hole through center ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .hole(hole_dia)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: tab_len = 0.863206
        expected_xlen = tab_len
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
    
        # Y extent: main_wid + 2 * tab_wid = 0.56638 + 2*0.141509 = 0.849398
        expected_ylen = main_wid + 2 * tab_wid
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
    
        # Z extent: height
        assert abs(bb.zlen - height) < TOL, \
            f"Z height: expected {height:.6f}, got {bb.zlen:.6f}"
    
        # Volume check
        # Cross shape area = main_len * main_wid + 2 * tab_len * tab_wid
        # (tabs don't overlap with main rect since they're outside)
        cross_area = main_len * main_wid + 2 * tab_len * tab_wid
        hole_area = math.pi * hole_rad ** 2
        expected_vol = (cross_area - hole_area) * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical face exists (the hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Expected at least 1 cylindrical face (hole), got {cyl_faces}"
    
        # Check hole goes through: center point at mid-height should be outside solid
        center_in_hole = result.val().isInside((0, 0, height / 2))
        assert not center_in_hole, \
            "Center point should be outside solid (inside hole), but isInside returned True"
    
        # Check a point clearly inside the main body (outside hole radius) is inside the solid
        # hole_rad = 0.159198, so use x=0.25 which is > hole_rad but < main_len/2 = 0.318396
        inside_x = 0.25
        inside_pt = result.val().isInside((inside_x, 0, height / 2))
        assert inside_pt, \
            f"Point ({inside_x}, 0, {height/2:.4f}) should be inside solid (outside hole, inside main rect), but isInside returned False"
    
        # Check tab regions are part of the solid
        tab_pt_top = result.val().isInside((0, tab_y_offset, height / 2))
        assert tab_pt_top, \
            f"Point in top tab should be inside solid, but isInside returned False"
    
        tab_pt_bot = result.val().isInside((0, -tab_y_offset, height / 2))
        assert tab_pt_bot, \
            f"Point in bottom tab should be inside solid, but isInside returned False"
    
        # Check symmetry: center of mass should be near (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X should be ~0, got {com.x:.6f}"
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0, got {com.y:.6f}"
        assert abs(com.z - height / 2) < TOL, \
            f"Center of mass Z should be ~{height/2:.6f}, got {com.z:.6f}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997071/gpt_generated.stl')
