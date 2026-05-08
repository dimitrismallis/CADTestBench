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
        plate_length = 200.0   # X direction
        plate_width  = 80.0    # Y direction
        plate_height = 5.0     # Z direction (thickness)
    
        hole_diameter = 10.0
        hole_radius   = hole_diameter / 2.0
    
        # Near top-left corner:
        # "top" in XY plane = max Y side, "left" = min X side
        # Holes aligned along X (length), near top-left
        x_start_offset = 20.0   # distance from left edge to first hole center
        y_offset_from_top = 15.0  # distance from top edge to hole centers
        hole_spacing = 20.0      # center-to-center spacing along X
    
        # Plate is centered at origin by default in CadQuery
        # So X ranges from -100 to +100, Y ranges from -40 to +40
        plate_x_min = -plate_length / 2.0
        plate_y_max = plate_width / 2.0
    
        # Hole centers in absolute coordinates
        hole_y = plate_y_max - y_offset_from_top  # near top edge
        hole_x1 = plate_x_min + x_start_offset
        hole_x2 = hole_x1 + hole_spacing
        hole_x3 = hole_x2 + hole_spacing
    
        hole_centers = [(hole_x1, hole_y), (hole_x2, hole_y), (hole_x3, hole_y)]
    
        # --- Step 1: Create the rectangular base plate ---
        result = cq.Workplane("XY").box(plate_length, plate_width, plate_height)
    
        # --- Step 2: Cut three circular holes near the top-left corner ---
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints(hole_centers)
            .hole(hole_diameter)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - plate_length) < TOL, \
            f"X length: expected {plate_length}, got {bb.xlen}"
        assert abs(bb.ylen - plate_width) < TOL, \
            f"Y width: expected {plate_width}, got {bb.ylen}"
        assert abs(bb.zlen - plate_height) < TOL, \
            f"Z height: expected {plate_height}, got {bb.zlen}"
    
        # Check volume: plate minus three cylindrical holes
        solid_vol = plate_length * plate_width * plate_height
        hole_vol  = 3 * math.pi * hole_radius**2 * plate_height
        expected_vol = solid_vol - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check cylindrical faces: 3 holes × 1 cylindrical face each = 3
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 3, \
            f"Cylindrical faces: expected 3, got {cyl_faces}"
    
        # Check circular edges: each hole has 2 circular edges (top and bottom) = 6 total
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 6, \
            f"Circular edges: expected 6, got {circ_edges}"
    
        # Verify holes exist using isInside:
        # A point at the center of each hole (mid-height) should be OUTSIDE the solid
        shape = result.val()
        mid_z = 0.0  # mid-height of plate (centered at z=0)
        for (hx, hy) in hole_centers:
            point_in_hole = cq.Vector(hx, hy, mid_z)
            assert not shape.isInside(point_in_hole), \
                f"Point ({hx},{hy},{mid_z}) should be outside solid (inside hole), but isInside returned True"
    
        # Verify solid material exists between holes (a point between hole 1 and hole 2)
        between_x = (hole_x1 + hole_x2) / 2.0
        # Offset slightly in Y away from hole center to be in solid material
        between_y = hole_y - hole_radius - 2.0
        point_in_solid = cq.Vector(between_x, between_y, mid_z)
        assert shape.isInside(point_in_solid), \
            f"Point ({between_x},{between_y},{mid_z}) should be inside solid, but isInside returned False"
    
        # Verify holes are near top-left: all hole Y coords should be > 0 (upper half)
        assert hole_y > 0, \
            f"Holes should be in upper half (Y>0), got hole_y={hole_y}"
    
        # All hole X coords should be in left half (< 0)
        assert all(hx < 0 for hx, _ in hole_centers), \
            f"Holes should be in left half (X<0), got X coords: {[hx for hx,_ in hole_centers]}"
    
        # Verify holes are aligned along X (same Y)
        ys = [hy for _, hy in hole_centers]
        assert all(abs(y - ys[0]) < TOL for y in ys), \
            f"All holes should have same Y coordinate, got: {ys}"
    
        # Verify spacing between consecutive holes
        xs = [hx for hx, _ in hole_centers]
        assert abs(xs[1] - xs[0] - hole_spacing) < TOL, \
            f"Spacing between hole 1 and 2: expected {hole_spacing}, got {xs[1]-xs[0]}"
        assert abs(xs[2] - xs[1] - hole_spacing) < TOL, \
            f"Spacing between hole 2 and 3: expected {hole_spacing}, got {xs[2]-xs[1]}"
    
        # Verify holes are much smaller than the plate
        assert hole_diameter < plate_length / 5, \
            f"Holes should be much smaller than plate length: {hole_diameter} vs {plate_length}"
        assert hole_diameter < plate_width / 5, \
            f"Holes should be much smaller than plate width: {hole_diameter} vs {plate_width}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00984033/gpt_generated.stl')
