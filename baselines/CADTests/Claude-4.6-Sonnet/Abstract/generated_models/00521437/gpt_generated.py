import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        base_w   = 120.0   # width  (X), ratio = 12:1 with height
        base_h   = 10.0    # height (Y)
        base_t   = 3.0     # extrusion thickness (Z)
    
        hole_w   = 45.0    # each hole width  (X) — slightly less than half of 120=60
        hole_h   = 6.0     # each hole height (Y) — slightly less than base_h=10
        hole_t   = base_t  # cut all the way through
    
        # Layout in X:
        #   left_margin(5) | hole_w(45) | center_gap(20) | hole_w(45) | right_margin(5)
        left_margin = 5.0
        # center_gap = 120 - 2*45 - 2*5 = 20  (verified > 0)
    
        # Hole centres (symmetric about X=0, Y=0, Z=base_t/2)
        hole_cx_left  = -base_w/2 + left_margin + hole_w/2   # -60+5+22.5 = -32.5
        hole_cx_right = +base_w/2 - left_margin - hole_w/2   # +60-5-22.5 = +32.5
        hole_cy       =  0.0
        hole_cz       =  base_t / 2   # 1.5
    
        # --- Step 1: Base extruded rectangle (120 x 10 x 3 mm) ---
        base = (
            cq.Workplane("XY")
            .rect(base_w, base_h)
            .extrude(base_t)
        )
    
        # --- Step 2: Create hole cutters as explicit boxes ---
        left_hole_cutter = (
            cq.Workplane("XY")
            .box(hole_w, hole_h, hole_t,
                 centered=(True, True, True))
            .translate((hole_cx_left, hole_cy, hole_cz))
        )
    
        right_hole_cutter = (
            cq.Workplane("XY")
            .box(hole_w, hole_h, hole_t,
                 centered=(True, True, True))
            .translate((hole_cx_right, hole_cy, hole_cz))
        )
    
        # --- Step 3: Subtract holes from base ---
        result = base.cut(left_hole_cutter).cut(right_hole_cutter)
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # 1. Bounding box matches base rectangle
        assert abs(bb.xlen - base_w) < TOL, \
            f"X length: expected {base_w}, got {bb.xlen}"
        assert abs(bb.ylen - base_h) < TOL, \
            f"Y length: expected {base_h}, got {bb.ylen}"
        assert abs(bb.zlen - base_t) < TOL, \
            f"Z length: expected {base_t}, got {bb.zlen}"
    
        # 2. Width-to-height ratio is 10–15×
        ratio = base_w / base_h
        assert 10 <= ratio <= 15, \
            f"Width/height ratio: expected 10–15, got {ratio}"
    
        # 3. Volume: base minus two rectangular holes
        base_vol     = base_w * base_h * base_t     # 120*10*3 = 3600
        hole_vol     = 2 * hole_w * hole_h * hole_t # 2*45*6*3 = 1620
        expected_vol = base_vol - hole_vol           # 1980
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 4. Each hole area is slightly less than half the base rectangle face area
        base_face_area = base_w * base_h   # 1200
        hole_face_area = hole_w * hole_h   # 270
        half_base_area = base_face_area / 2  # 600
        assert hole_face_area < half_base_area, \
            f"Each hole area ({hole_face_area}) should be < half base area ({half_base_area})"
        assert hole_face_area > 0.3 * half_base_area, \
            f"Each hole area ({hole_face_area}) seems too small vs half base ({half_base_area})"
    
        # 5. Holes don't touch each other (positive inter-hole gap)
        left_hole_right_edge  = hole_cx_left  + hole_w / 2   # -32.5 + 22.5 = -10
        right_hole_left_edge  = hole_cx_right - hole_w / 2   #  32.5 - 22.5 = +10
        actual_inter_gap = right_hole_left_edge - left_hole_right_edge  # 20
        assert actual_inter_gap > 0, \
            f"Holes touch or overlap! Inter-hole gap = {actual_inter_gap}"
    
        # 6. Holes don't touch left/right edges of base
        left_hole_left_edge   = hole_cx_left  - hole_w / 2   # -55
        right_hole_right_edge = hole_cx_right + hole_w / 2   # +55
        margin_left  = left_hole_left_edge  - (-base_w / 2)  # 5
        margin_right = (base_w / 2) - right_hole_right_edge  # 5
        assert margin_left  > 0, f"Left hole touches left edge! margin = {margin_left}"
        assert margin_right > 0, f"Right hole touches right edge! margin = {margin_right}"
    
        # 7. Holes don't touch top/bottom edges of base
        top_bottom_margin = base_h / 2 - hole_h / 2   # 5 - 3 = 2
        assert top_bottom_margin > 0, \
            f"Holes touch top/bottom edge! margin = {top_bottom_margin}"
    
        # 8. Symmetry: centre of mass should be at (0, 0, base_t/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"CoM X not centred: expected 0, got {com.x}"
        assert abs(com.y) < TOL, \
            f"CoM Y not centred: expected 0, got {com.y}"
        assert abs(com.z - base_t / 2) < TOL, \
            f"CoM Z: expected {base_t/2}, got {com.z}"
    
        # 9. No cylindrical faces (all holes are rectangular)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, \
            f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # 10. Points inside holes are NOT inside the solid
        solid = result.val()
        left_hole_pt  = (hole_cx_left,  hole_cy, hole_cz)
        right_hole_pt = (hole_cx_right, hole_cy, hole_cz)
        assert not solid.isInside(left_hole_pt), \
            f"Left hole centre {left_hole_pt} should be outside solid (it's a hole)"
        assert not solid.isInside(right_hole_pt), \
            f"Right hole centre {right_hole_pt} should be outside solid (it's a hole)"
    
        # 11. A point in the solid body (between holes, at mid-Z) IS inside
        body_pt = (0.0, 0.0, hole_cz)
        assert solid.isInside(body_pt), \
            f"Body centre {body_pt} should be inside solid"
    
        # 12. A point outside the solid entirely is NOT inside
        outside_pt = (0.0, 0.0, base_t + 1.0)
        assert not solid.isInside(outside_pt), \
            f"Point above solid {outside_pt} should be outside solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00521437/gpt_generated.stl')
