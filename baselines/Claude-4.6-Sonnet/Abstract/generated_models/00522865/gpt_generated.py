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
        # Base rectangle
        base_l = 80.0
        base_w = 40.0
        base_h = 4.0
    
        # Hollow: half the size of original
        hollow_l = base_l / 2   # 40
        hollow_w = base_w / 2   # 20
    
        # Top rectangle: 3/4 size, 1/4 extrusion
        top_l = base_l * 3 / 4   # 60
        top_w = base_w * 3 / 4   # 30
        top_h = base_h / 4        # 1
    
        # Tiny rectangles
        tiny_l = 4.0
        tiny_w = 3.0
        tiny_h = top_h  # same extrusion as top plate
    
        # Offset: on either side of first line of symmetry (X-axis of top rect)
        # "slightly below second line of symmetry" → slightly in -Y from center of top rect
        tiny_x_offset = top_l / 4   # 15 units from center along X
        tiny_y_offset = -top_w / 4  # slightly below center along Y (below second line of symmetry)
    
        # --- Step 1: Base rectangle extruded ---
        result = cq.Workplane("XY").rect(base_l, base_w).extrude(base_h)
    
        # --- Step 2: Central rectangular hollow (half size), cut through base ---
        result = (
            result
            .faces(">Z").workplane()
            .rect(hollow_l, hollow_w)
            .cutBlind(-base_h)
        )
    
        # --- Step 3: Top rectangle (3/4 size, 1/4 extrusion) centered on top ---
        result = (
            result
            .faces(">Z").workplane()
            .rect(top_l, top_w)
            .extrude(top_h)
        )
    
        # --- Step 4: Two tiny rectangles on either side of top rect's first line of symmetry,
        #             slightly below its second line of symmetry ---
        # The top plate sits at z = base_h to base_h + top_h
        # We place tiny rects on the top face of the top plate
        top_face_z = base_h + top_h
    
        # Left tiny rect: at (-tiny_x_offset, tiny_y_offset)
        # Right tiny rect: at (+tiny_x_offset, tiny_y_offset)
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([(-tiny_x_offset, tiny_y_offset), (tiny_x_offset, tiny_y_offset)])
            .rect(tiny_l, tiny_w)
            .extrude(tiny_h)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box: X should be base_l=80, Y should be base_w=40
        assert abs(bb.xlen - base_l) < TOL, f"X extent: expected {base_l}, got {bb.xlen}"
        assert abs(bb.ylen - base_w) < TOL, f"Y extent: expected {base_w}, got {bb.ylen}"
    
        # Total Z height: base_h + top_h + tiny_h = 4 + 1 + 1 = 6
        expected_total_z = base_h + top_h + tiny_h
        assert abs(bb.zlen - expected_total_z) < TOL, f"Z extent: expected {expected_total_z}, got {bb.zlen}"
    
        # Z min should be 0 (base sits on XY plane)
        assert abs(bb.zmin) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - expected_total_z) < TOL, f"Z max: expected {expected_total_z}, got {bb.zmax}"
    
        # Volume check:
        # Base volume = base_l * base_w * base_h - hollow_l * hollow_w * base_h
        base_vol = base_l * base_w * base_h - hollow_l * hollow_w * base_h
        # Top plate volume = top_l * top_w * top_h
        top_vol = top_l * top_w * top_h
        # Two tiny rects volume = 2 * tiny_l * tiny_w * tiny_h
        tiny_vol = 2 * tiny_l * tiny_w * tiny_h
        expected_vol = base_vol + top_vol + tiny_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check hollow exists: a point at center of base should be outside (hollow goes through)
        center_point = (0, 0, base_h / 2)
        assert not result.val().isInside(center_point), \
            f"Center of base should be hollow (outside solid), but isInside returned True"
    
        # Check top plate exists: a point at center top plate level should be inside
        top_plate_point = (0, 0, base_h + top_h / 2)
        assert result.val().isInside(top_plate_point), \
            f"Center of top plate should be inside solid"
    
        # Check tiny rects exist: points inside tiny rect volumes should be inside solid
        tiny_left_point = (-tiny_x_offset, tiny_y_offset, base_h + top_h + tiny_h / 2)
        tiny_right_point = (tiny_x_offset, tiny_y_offset, base_h + top_h + tiny_h / 2)
        assert result.val().isInside(tiny_left_point), \
            f"Left tiny rect center should be inside solid"
        assert result.val().isInside(tiny_right_point), \
            f"Right tiny rect center should be inside solid"
    
        # Cylindrical faces: none expected (all rectangular)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00522865/gpt_generated.stl')
