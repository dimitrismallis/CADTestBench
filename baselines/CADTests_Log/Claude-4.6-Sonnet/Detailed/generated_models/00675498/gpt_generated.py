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
        rect_w = 0.75          # rectangle width (X direction)
        rect_h = 0.664347      # rectangle height (Y direction)
        trap_height = 0.374227 # trapezoid height (extends in +X from rectangle right edge)
        trap_long   = 0.562673 # longer base of trapezoid (along Y, attached to rectangle)
        trap_short  = 0.280836 # shorter base of trapezoid (along Y, far end)
        extrude_d   = 0.664347 # extrusion depth (Z direction)
    
        # --- Step 1: Build the combined 2D profile as a closed polygon ---
        # The profile consists of:
        #   - Rectangle: (0,0) to (rect_w, rect_h)
        #   - Right trapezoid attached to the right end of the rectangle
        #     with longer base along the rectangle's right edge (from y=0 to y=trap_long)
        #     extending rightward by trap_height, with shorter base = trap_short
        #
        # Vertices (counter-clockwise):
        # P0 = (0, 0)                                  bottom-left of rectangle
        # P1 = (rect_w, 0)                             bottom-right of rectangle / bottom-left of trapezoid
        # P2 = (rect_w + trap_height, 0)               bottom-right of trapezoid (right angle here)
        # P3 = (rect_w + trap_height, trap_short)      top-right of trapezoid (shorter base end)
        # P4 = (rect_w, trap_long)                     top-left of trapezoid = point on rectangle right edge
        # P5 = (rect_w, rect_h)                        top-right of rectangle
        # P6 = (0, rect_h)                             top-left of rectangle
        #
        # Note: P0->P1->P2 are collinear (all on y=0), so the bottom is one merged face.
        # Similarly, P4->P5 are collinear (both on x=rect_w), so the right side is one merged face.
        # This gives 5 distinct side faces + 2 end caps = 7... let's count carefully:
        #
        # Distinct edges after collinear merging:
        #   Bottom: P0 -> P2 (merged P0->P1->P2, all y=0)
        #   Right-bottom: P2 -> P3 (vertical, x=rect_w+trap_height)
        #   Slant: P3 -> P4
        #   Right-top: P4 -> P5 (merged P4->P5, both x=rect_w) -- wait, P4=(rect_w, trap_long), P5=(rect_w, rect_h)
        #              these are collinear with P1=(rect_w,0) only if same x. P4 and P5 share x=rect_w but
        #              P1 is also at x=rect_w. However P1->P2 goes in +X direction, so P4->P5 is a separate segment.
        #   Top: P5 -> P6
        #   Left: P6 -> P0
        #
        # So merged edges: bottom (P0->P1->P2 = 1 face), right-step (P4->P5 stays as is)
        # Total side faces = 6, end caps = 2, total = 8. This matches the observed count of 8.
    
        pts = [
            (0,                       0),
            (rect_w,                  0),
            (rect_w + trap_height,    0),
            (rect_w + trap_height,    trap_short),
            (rect_w,                  trap_long),
            (rect_w,                  rect_h),
            (0,                       rect_h),
        ]
    
        # --- Step 2: Create the profile and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .lineTo(pts[5][0], pts[5][1])
            .lineTo(pts[6][0], pts[6][1])
            .close()
            .extrude(extrude_d)
        )
    
        # --- Final object verification ---
        TOL = 1e-3
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        expected_xlen = rect_w + trap_height  # 0.75 + 0.374227 = 1.124227
        expected_ylen = rect_h                # 0.664347
        expected_zlen = extrude_d             # 0.664347
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Volume check
        # Profile area = rectangle area + trapezoid area
        rect_area = rect_w * rect_h
        trap_area  = 0.5 * (trap_long + trap_short) * trap_height
        profile_area = rect_area + trap_area
        expected_vol = profile_area * extrude_d
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count:
        # The polygon has 7 input edges, but P0->P1->P2 are collinear (all on y=0),
        # so they merge into one bottom face. This gives 6 side faces + 2 end caps = 8 total.
        face_count = result.faces().size()
        assert face_count == 8, \
            f"Face count: expected 8, got {face_count}"
    
        # The object should have no cylindrical faces (all planar)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, \
            f"Cylindrical faces: expected 0, got {cyl_faces}"
    
        # Check bounding box origin (should start at 0,0,0)
        assert abs(bb.xmin - 0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.zmin - 0) < TOL, f"zmin: expected 0, got {bb.zmin}"
    
        # Check a point inside the rectangle portion is inside the solid
        inside_rect = (rect_w / 2, rect_h / 2, extrude_d / 2)
        assert result.val().isInside(inside_rect), \
            f"Point {inside_rect} should be inside the solid (rectangle region)"
    
        # Check a point inside the trapezoid portion is inside the solid
        inside_trap = (rect_w + trap_height / 2, trap_short / 4, extrude_d / 2)
        assert result.val().isInside(inside_trap), \
            f"Point {inside_trap} should be inside the solid (trapezoid region)"
    
        # Check a point outside (above the trapezoid's slanted edge) is outside
        outside_pt = (rect_w + trap_height / 2, trap_long, extrude_d / 2)
        assert not result.val().isInside(outside_pt), \
            f"Point {outside_pt} should be outside the solid"
    
        # Check that the step/tier is present: a point above trap_long but within rect_h
        # and within rect_w should be inside (it's in the rectangle region)
        inside_upper_rect = (rect_w / 2, (trap_long + rect_h) / 2, extrude_d / 2)
        assert result.val().isInside(inside_upper_rect), \
            f"Point {inside_upper_rect} should be inside the solid (upper rectangle region)"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00675498/gpt_generated.stl')
