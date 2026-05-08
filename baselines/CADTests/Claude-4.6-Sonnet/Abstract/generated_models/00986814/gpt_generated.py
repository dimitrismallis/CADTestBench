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
        rect_length = 80.0   # X direction
        rect_width  = 20.0   # Y direction
        extrude_h   = 5.0    # extrusion height for both base and cylinders
        cyl_radius  = 4.0    # radius of each small cylinder
        cyl_spacing = 10.0   # center-to-center spacing of the two cylinders along Y
        # Place cylinders near one end of the rectangle (+X end)
        cyl_x = rect_length / 2 - 10.0   # x = 30 (near the +X end)
        cyl_y1 =  cyl_spacing / 2         # y = +5
        cyl_y2 = -cyl_spacing / 2         # y = -5
    
        # --- Step 1: Create the base rectangle and extrude it ---
        base = (
            cq.Workplane("XY")
            .rect(rect_length, rect_width)
            .extrude(extrude_h)
        )
    
        # --- Step 2: On the top face of the base, draw two small circles near one end ---
        # and extrude them upward by the same height
        result = (
            base
            .faces(">Z")
            .workplane()
            .pushPoints([(cyl_x, cyl_y1), (cyl_x, cyl_y2)])
            .circle(cyl_radius)
            .extrude(extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - rect_length) < TOL, \
            f"X length: expected {rect_length}, got {bb.xlen}"
        assert abs(bb.ylen - rect_width) < TOL, \
            f"Y length: expected {rect_width}, got {bb.ylen}"
        # Total Z = base height + cylinder height = 5 + 5 = 10
        expected_zlen = extrude_h + extrude_h
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # 2. Volume check
        base_vol = rect_length * rect_width * extrude_h
        cyl_vol  = 2 * math.pi * cyl_radius**2 * extrude_h
        expected_vol = base_vol + cyl_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical faces: 2 cylinders → 2 curved side faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # 4. Check that the cylinders are on the correct end (near +X)
        # The bounding box max X should equal rect_length/2
        assert abs(bb.xmax - rect_length / 2) < TOL, \
            f"xmax: expected {rect_length/2}, got {bb.xmax}"
        assert abs(bb.xmin + rect_length / 2) < TOL, \
            f"xmin: expected {-rect_length/2}, got {bb.xmin}"
    
        # 5. Check top faces exist at z = extrude_h * 2 (cylinder tops)
        top_faces = result.faces(">Z").size()
        assert top_faces >= 2, \
            f"Top faces (cylinder tops): expected at least 2, got {top_faces}"
    
        # 6. Check that cylinder centers are inside the solid
        solid = result.val()
        pt1 = (cyl_x, cyl_y1, extrude_h + extrude_h / 2)
        pt2 = (cyl_x, cyl_y2, extrude_h + extrude_h / 2)
        assert solid.isInside(pt1), \
            f"Point {pt1} should be inside the solid (cylinder 1 center)"
        assert solid.isInside(pt2), \
            f"Point {pt2} should be inside the solid (cylinder 2 center)"
    
        # 7. Check that a point far from the cylinders (other end) is NOT above base height
        # i.e., the other end of the rectangle has no cylinder
        far_pt = (-rect_length / 2 + 5, 0, extrude_h + 1)
        assert not solid.isInside(far_pt), \
            f"Point {far_pt} should NOT be inside the solid (no cylinder at far end)"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00986814/gpt_generated.stl')
