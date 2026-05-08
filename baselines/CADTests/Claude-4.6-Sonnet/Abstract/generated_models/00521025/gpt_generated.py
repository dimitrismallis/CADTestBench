import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        rect_w = 80.0       # base rectangle width (X)
        rect_h = 40.0       # base rectangle height (Y)
        extrude_d = 5.0     # slight extrusion depth (Z)
    
        hole_w = rect_w / 8.0   # 10.0 mm — hole width (X), horizontal orientation
        hole_h = rect_h / 8.0   # 5.0 mm  — hole height (Y)
    
        # Hole center: horizontally centered (x=0), near bottom of rectangle
        # Bottom edge of base rect is at y = -rect_h/2 = -20
        # Place hole center so there's a small margin from the bottom edge
        margin = 4.0
        hole_center_y = -rect_h / 2.0 + margin + hole_h / 2.0  # = -20 + 4 + 2.5 = -13.5
    
        # --- Step 1: Create base rectangle extruded slightly ---
        result = cq.Workplane("XY").rect(rect_w, rect_h).extrude(extrude_d)
    
        # --- Step 2: Create rectangular hole centered near bottom, horizontal ---
        # Work on the top face, position hole at (0, hole_center_y)
        result = (
            result
            .faces(">Z").workplane()
            .center(0, hole_center_y)
            .rect(hole_w, hole_h)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box: should still be 80 x 40 x 5 (hole doesn't change outer dims)
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - rect_w) < TOL, f"BB xlen: expected {rect_w}, got {bb.xlen}"
        assert abs(bb.ylen - rect_h) < TOL, f"BB ylen: expected {rect_h}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_d) < TOL, f"BB zlen: expected {extrude_d}, got {bb.zlen}"
    
        # Volume: base box minus rectangular hole
        base_vol = rect_w * rect_h * extrude_d          # 80*40*5 = 16000
        hole_vol = hole_w * hole_h * extrude_d           # 10*5*5  = 250
        expected_vol = base_vol - hole_vol               # 15750
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Hole dimensions: 1/8th of original rectangle dimensions
        assert abs(hole_w - rect_w / 8.0) < TOL, f"Hole width should be rect_w/8 = {rect_w/8}, got {hole_w}"
        assert abs(hole_h - rect_h / 8.0) < TOL, f"Hole height should be rect_h/8 = {rect_h/8}, got {hole_h}"
    
        # Hole is horizontal: hole_w > hole_h (wider than tall)
        assert hole_w > hole_h, f"Hole should be horizontal (wider than tall): {hole_w} > {hole_h}"
    
        # Hole is near the bottom: center Y is in the lower half of the rectangle
        assert hole_center_y < 0, f"Hole center Y should be negative (lower half): {hole_center_y}"
        assert hole_center_y > -rect_h / 2.0, f"Hole center Y should be inside rectangle: {hole_center_y}"
    
        # Check that a point inside the hole is NOT inside the solid (it's a through-hole)
        hole_center_z = extrude_d / 2.0
        point_in_hole = (0.0, hole_center_y, hole_center_z)
        solid = result.val()
        assert not solid.isInside(point_in_hole), \
            f"Point {point_in_hole} should be inside the hole (not solid material)"
    
        # Check that a point outside the hole (but inside the base rect) IS inside the solid
        point_in_solid = (0.0, rect_h / 2.0 - 2.0, hole_center_z)  # near top edge
        assert solid.isInside(point_in_solid), \
            f"Point {point_in_solid} should be inside the solid material"
    
        # Face count: base box has 6 faces, hole adds 4 side faces + 2 inner edge loops
        # A rectangular through-hole in a box adds 4 rectangular faces (the tunnel walls)
        # Total faces = 6 (box) + 4 (hole walls) = 10
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # The top and bottom faces should each have a rectangular hole (inner wire)
        # Check there are exactly 2 faces with normal in Z direction (top and bottom)
        z_faces = result.faces("|Z").size()
        assert z_faces == 2, f"Z-parallel faces: expected 2 (top+bottom), got {z_faces}"
    
        print(f"All assertions passed!")
        print(f"  Base rectangle: {rect_w} x {rect_h} mm, extruded {extrude_d} mm")
        print(f"  Hole: {hole_w} x {hole_h} mm (1/8th of base dimensions)")
        print(f"  Hole center Y: {hole_center_y} mm (near bottom)")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f} mm³)")
        print(f"  Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00521025/gpt_generated.stl')
