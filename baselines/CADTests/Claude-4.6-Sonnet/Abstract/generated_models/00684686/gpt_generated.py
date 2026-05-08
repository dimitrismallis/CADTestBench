import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        plate_w = 80.0    # plate width (X)
        plate_d = 40.0    # plate depth (Y)
        plate_h = 5.0     # plate height (Z, slight extrusion)
    
        hole_w = 40.0     # hole width (X) — 1/4 area of plate
        hole_d = 20.0     # hole depth (Y) — 1/4 area of plate
        gap    = 3.0      # small gap between hole bottom edge and plate bottom edge
    
        # --- Step 1: Create the base rectangular plate ---
        # Box centered at origin: X in [-40,40], Y in [-20,20], Z in [0, 5]
        result = cq.Workplane("XY").rect(plate_w, plate_d).extrude(plate_h)
    
        # --- Step 2 & 3: Place inner rectangle and cut through ---
        # Plate bottom edge in Y is at -plate_d/2 = -20
        # We want a gap of 3mm, so hole bottom edge at Y = -20 + 3 = -17
        # Hole depth = 20, so hole center in Y = -17 + hole_d/2 = -17 + 10 = -7
        hole_center_y = -plate_d / 2 + gap + hole_d / 2  # = -20 + 3 + 10 = -7
        hole_center_x = 0.0  # centered in X
    
        # Work on the top face, then cut downward through the full plate
        result = (
            result
            .faces(">Z").workplane()
            .center(hole_center_x, hole_center_y)
            .rect(hole_w, hole_d)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box: plate dimensions unchanged
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - plate_w) < TOL, f"X length: expected {plate_w}, got {bb.xlen}"
        assert abs(bb.ylen - plate_d) < TOL, f"Y length: expected {plate_d}, got {bb.ylen}"
        assert abs(bb.zlen - plate_h) < TOL, f"Z length: expected {plate_h}, got {bb.zlen}"
    
        # 2. Volume: plate volume minus hole volume
        plate_vol = plate_w * plate_d * plate_h
        hole_vol  = hole_w * hole_d * plate_h
        expected_vol = plate_vol - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. No cylindrical faces — all geometry is planar (rectangular hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # 4. Check planar faces count:
        # - Top face: 1 (with inner hole loop, but still one face)
        # - Bottom face: 1 (with inner hole loop, but still one face)
        # - 4 outer side walls: 4 faces
        # - 4 inner hole walls: 4 faces
        # Total: 10 planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 10, f"Expected 10 planar faces, got {planar_faces}"
    
        # 5. Verify the hole exists: a point inside the hole region should NOT be inside the solid
        # Hole center at (0, -7, 2.5) — inside the hole, so not inside solid
        hole_interior_pt = (hole_center_x, hole_center_y, plate_h / 2)
        assert not result.val().isInside(hole_interior_pt), \
            f"Point {hole_interior_pt} should be outside (in the hole), but isInside returned True"
    
        # 6. Verify a point in the solid plate (away from hole) IS inside
        # Near the top edge in Y (positive Y side), well within plate bounds
        solid_pt = (0.0, plate_d / 2 - 2.0, plate_h / 2)
        assert result.val().isInside(solid_pt), \
            f"Point {solid_pt} should be inside the solid, but isInside returned False"
    
        # 7. Verify gap region: a point in the gap (between hole bottom and plate bottom) is inside solid
        # Gap region: Y in [-20, -17], pick Y = -18.5 (midpoint of gap)
        gap_pt = (0.0, -plate_d / 2 + gap / 2, plate_h / 2)  # Y = -18.5
        assert result.val().isInside(gap_pt), \
            f"Gap point {gap_pt} should be inside the solid (gap region), but isInside returned False"
    
        # 8. Verify a point inside the hole (above gap, within hole bounds) is NOT in solid
        # Y = -16 is inside hole (hole spans Y: -17 to 3), X=0, Z=mid
        inside_hole_pt = (0.0, -plate_d / 2 + gap + 1.0, plate_h / 2)  # Y = -16
        assert not result.val().isInside(inside_hole_pt), \
            f"Point {inside_hole_pt} should be in the hole (not solid), but isInside returned True"
    
        # 9. Verify hole top edge boundary: hole top is at Y = -7 + 10 = 3
        # A point at Y = 2 (inside hole) should not be in solid
        inside_hole_top = (0.0, hole_center_y + hole_d / 2 - 1.0, plate_h / 2)  # Y = 2
        assert not result.val().isInside(inside_hole_top), \
            f"Point {inside_hole_top} should be in the hole, but isInside returned True"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00684686/gpt_generated.stl')
