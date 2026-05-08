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
        rect_w      = 100.0   # rectangle width  (X)
        rect_h      = 60.0    # rectangle height (Y)
        thickness   = 10.0    # extrusion height (Z)
    
        large_d     = 30.0    # large center hole diameter
        small_d     = 12.0    # small hole diameter
        small_off_x = 35.0    # X offset of small holes from center
    
        # --- Step 1: Base rectangle extruded ---
        result = (
            cq.Workplane("XY")
            .rect(rect_w, rect_h)
            .extrude(thickness)
        )
    
        # --- Step 2: Large circle hole at center ---
        result = (
            result
            .faces(">Z").workplane()
            .moveTo(0, 0)
            .circle(large_d / 2)
            .cutThruAll()
        )
    
        # --- Step 3: Small circle hole on the LEFT (−X) ---
        result = (
            result
            .faces(">Z").workplane()
            .moveTo(-small_off_x, 0)
            .circle(small_d / 2)
            .cutThruAll()
        )
    
        # --- Step 4: Small circle hole on the RIGHT (+X) ---
        result = (
            result
            .faces(">Z").workplane()
            .moveTo(small_off_x, 0)
            .circle(small_d / 2)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.05
    
        # 1. Bounding box matches the original rectangle extruded
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - rect_w)    < TOL, f"X length: expected {rect_w}, got {bb.xlen}"
        assert abs(bb.ylen - rect_h)    < TOL, f"Y length: expected {rect_h}, got {bb.ylen}"
        assert abs(bb.zlen - thickness) < TOL, f"Z length: expected {thickness}, got {bb.zlen}"
    
        # 2. Volume: box minus three cylindrical holes
        box_vol        = rect_w * rect_h * thickness
        large_hole_vol = math.pi * (large_d / 2) ** 2 * thickness
        small_hole_vol = math.pi * (small_d / 2) ** 2 * thickness
        expected_vol   = box_vol - large_hole_vol - 2 * small_hole_vol
        actual_vol     = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Three cylindrical faces (one per hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 3, f"Cylindrical faces: expected 3, got {cyl_faces}"
    
        # 4. Three circular edges on the top face (one per hole opening)
        top_circ_edges = result.faces(">Z").edges("%Circle").size()
        assert top_circ_edges == 3, \
            f"Circular edges on top face: expected 3, got {top_circ_edges}"
    
        # 5. Center of mass should be at the geometric center (x=0, y=0, z=thickness/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - thickness / 2) < TOL, f"CoM Z: expected {thickness/2}, got {com.z}"
    
        # 6. Large hole passes through center: a point at center should be OUTSIDE (inside the hole)
        center_point = (0, 0, thickness / 2)
        assert not result.val().isInside(center_point), \
            "Center point should be inside the large hole (outside the solid)"
    
        # 7. Small holes pass through: points at (±small_off_x, 0, thickness/2) should be outside
        left_point  = (-small_off_x, 0, thickness / 2)
        right_point = ( small_off_x, 0, thickness / 2)
        assert not result.val().isInside(left_point), \
            "Left small hole center should be outside the solid"
        assert not result.val().isInside(right_point), \
            "Right small hole center should be outside the solid"
    
        # 8. A point in the solid body (not in any hole) should be inside
        solid_point = (0, rect_h / 2 - 5, thickness / 2)
        assert result.val().isInside(solid_point), \
            f"Point {solid_point} should be inside the solid body"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00034239/gpt_generated.stl')
