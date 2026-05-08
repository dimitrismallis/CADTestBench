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
        # Outer trapezoid (in XY plane, extruded in Z)
        outer_bottom = 60.0   # bottom base width
        outer_top    = 30.0   # top base width
        outer_height = 40.0   # height of trapezoid (in Y)
        extrude_depth = 20.0  # extrusion depth (in Z)
    
        # Inner trapezoid (hole) — smaller than outer
        inner_bottom = 40.0
        inner_top    = 20.0
        inner_height = 28.0
    
        # --- Step 1: Build outer trapezoid profile using a closed wire ---
        # Trapezoid vertices (centered in X, bottom at Y=0, top at Y=outer_height)
        # Bottom-left, bottom-right, top-right, top-left
        ob_half = outer_bottom / 2.0
        ot_half = outer_top    / 2.0
        oh      = outer_height
    
        outer_pts = [
            (-ob_half,  0.0),
            ( ob_half,  0.0),
            ( ot_half,  oh),
            (-ot_half,  oh),
        ]
    
        # --- Step 2: Extrude outer trapezoid ---
        outer = (
            cq.Workplane("XY")
            .moveTo(outer_pts[0][0], outer_pts[0][1])
            .lineTo(outer_pts[1][0], outer_pts[1][1])
            .lineTo(outer_pts[2][0], outer_pts[2][1])
            .lineTo(outer_pts[3][0], outer_pts[3][1])
            .close()
            .extrude(extrude_depth)
        )
    
        # --- Step 3: Build inner trapezoid profile for the hole ---
        # Centered the same way; slightly inset from outer
        ib_half = inner_bottom / 2.0
        it_half = inner_top    / 2.0
        ih      = inner_height
    
        # Vertical offset to center the inner trapezoid within the outer one
        # Outer height = 40, inner height = 28 → vertical margin = (40-28)/2 = 6
        y_offset = (outer_height - inner_height) / 2.0  # = 6.0
    
        inner_pts = [
            (-ib_half,  y_offset),
            ( ib_half,  y_offset),
            ( it_half,  y_offset + ih),
            (-it_half,  y_offset + ih),
        ]
    
        # Create the inner trapezoid as a cutter solid
        inner_cutter = (
            cq.Workplane("XY")
            .moveTo(inner_pts[0][0], inner_pts[0][1])
            .lineTo(inner_pts[1][0], inner_pts[1][1])
            .lineTo(inner_pts[2][0], inner_pts[2][1])
            .lineTo(inner_pts[3][0], inner_pts[3][1])
            .close()
            .extrude(extrude_depth)
        )
    
        # --- Step 4: Cut the inner trapezoid from the outer ---
        result = outer.cut(inner_cutter)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - outer_bottom) < TOL, \
            f"X extent: expected {outer_bottom}, got {bb.xlen}"
        assert abs(bb.ylen - outer_height) < TOL, \
            f"Y extent: expected {outer_height}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_depth) < TOL, \
            f"Z extent: expected {extrude_depth}, got {bb.zlen}"
    
        # 2. Volume check
        # Outer trapezoid area = 0.5 * (outer_bottom + outer_top) * outer_height
        outer_area = 0.5 * (outer_bottom + outer_top) * outer_height
        inner_area = 0.5 * (inner_bottom + inner_top) * inner_height
        expected_vol = (outer_area - inner_area) * extrude_depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # 3. Face count check
        # The solid is a trapezoid frame:
        # - 2 large planar faces (front Z=0 and back Z=20) — each is a trapezoid with a trapezoidal hole (annular)
        # - 4 outer side faces (planar, one per outer edge)
        # - 4 inner side faces (planar, one per inner edge)
        # Total = 2 + 4 + 4 = 10 planar faces
        face_count = result.faces().size()
        assert face_count == 10, \
            f"Face count: expected 10, got {face_count}"
    
        # 4. All faces should be planar (no cylinders)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 10, \
            f"Planar face count: expected 10, got {planar_count}"
    
        # 5. Check that the hole goes through: a point inside the inner trapezoid
        # should NOT be inside the solid
        # Center of inner trapezoid at mid-Z
        cx = 0.0
        cy = y_offset + ih / 2.0   # = 6 + 14 = 20
        cz = extrude_depth / 2.0   # = 10
        hole_center = (cx, cy, cz)
        assert not result.val().isInside(hole_center), \
            f"Point {hole_center} should be inside the hole (not in solid), but isInside returned True"
    
        # 6. Check that a point in the solid wall IS inside
        # Point in the bottom wall (between outer bottom and inner bottom)
        wall_pt = (0.0, y_offset / 2.0, cz)  # y = 3, in the bottom wall
        assert result.val().isInside(wall_pt), \
            f"Point {wall_pt} should be inside the solid wall, but isInside returned False"
    
        # 7. Symmetry: center of mass should be at x=0 (symmetric about YZ plane)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00985482/gpt_generated.stl')
