import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        rect_w   = 80.0   # rectangle width  (X)
        rect_h   = 50.0   # rectangle height (Y)
        thick    = 5.0    # extrusion thickness (Z)
        cut_size = 10.0   # side length of each corner square cutout
    
        # --- Step 1: Create the base rectangle sketch and extrude ---
        result = cq.Workplane("XY").rect(rect_w, rect_h).extrude(thick)
    
        # --- Step 2: Cut four corner squares ---
        # The rectangle is centered at origin, so corners are at (±40, ±25).
        # Each 10×10 square cutout is centered 5 mm inward from each corner,
        # i.e. at (±(rect_w/2 - cut_size/2), ±(rect_h/2 - cut_size/2)).
        half_w = rect_w / 2   # 40
        half_h = rect_h / 2   # 25
        offset = cut_size / 2  # 5  — half the cutout side
    
        corner_centers = [
            ( half_w - offset,  half_h - offset),   # top-right
            (-half_w + offset,  half_h - offset),   # top-left
            (-half_w + offset, -half_h + offset),   # bottom-left
            ( half_w - offset, -half_h + offset),   # bottom-right
        ]
    
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints(corner_centers)
            .rect(cut_size, cut_size)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box should still be the original rectangle dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - rect_w) < TOL, f"X length: expected {rect_w}, got {bb.xlen}"
        assert abs(bb.ylen - rect_h) < TOL, f"Y length: expected {rect_h}, got {bb.ylen}"
        assert abs(bb.zlen - thick)  < TOL, f"Z length: expected {thick},  got {bb.zlen}"
    
        # 2. Volume: base box minus four corner cutouts
        base_vol   = rect_w * rect_h * thick
        cutout_vol = 4 * (cut_size * cut_size * thick)
        expected_vol = base_vol - cutout_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Face count:
        #    - 1 top face (with 4 square holes → but it's still 1 face with inner wires)
        #    - 1 bottom face (same)
        #    - 4 outer side faces (the rectangle perimeter sides)
        #    - 4 × 3 inner side faces per cutout (each square cutout has 3 exposed inner walls
        #      since one side is flush with the outer edge — actually each corner cutout
        #      shares two sides with the outer boundary, so only 2 inner walls per cutout)
        # Let's count: each corner cutout exposes 2 inner vertical faces (the two sides
        # that are NOT on the outer boundary). So 4 cutouts × 2 = 8 inner side faces.
        # Total = 2 (top/bottom) + 4 (outer sides) + 8 (inner cutout walls) = 14 faces.
        face_count = result.faces().size()
        assert face_count == 14, f"Face count: expected 14, got {face_count}"
    
        # 4. The object should have exactly 4 cylindrical-free (all planar) faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 14, f"All faces should be planar, got {planar_faces}"
    
        # 5. Center of mass should be at the geometric center (0, 0, thick/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - thick / 2) < TOL, f"CoM Z: expected {thick/2}, got {com.z}"
    
        # 6. Verify corner points are NOT inside the solid (cutouts exist)
        corner_test_points = [
            ( half_w - offset,  half_h - offset, thick / 2),
            (-half_w + offset,  half_h - offset, thick / 2),
            (-half_w + offset, -half_h + offset, thick / 2),
            ( half_w - offset, -half_h + offset, thick / 2),
        ]
        for pt in corner_test_points:
            assert not result.val().isInside(pt), \
                f"Point {pt} should be inside a cutout (outside solid), but isInside returned True"
    
        # 7. Verify center of the plate IS inside the solid
        assert result.val().isInside((0, 0, thick / 2)), \
            "Center of plate should be inside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670274/gpt_generated.stl')
