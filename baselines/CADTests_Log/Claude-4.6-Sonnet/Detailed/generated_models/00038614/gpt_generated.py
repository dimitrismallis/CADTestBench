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
        outer_length  = 1.5
        outer_width   = 1.5
        padding       = 0.17649
        height        = 0.00265
    
        inner_length  = outer_length - 2 * padding   # 1.5 - 2*0.17649 = 1.14702
        inner_width   = outer_width  - 2 * padding   # 1.5 - 2*0.17649 = 1.14702
    
        # --- Step 1: Create outer rectangle profile ---
        outer_rect = cq.Workplane("XY").rect(outer_length, outer_width)
    
        # --- Step 2: Subtract inner rectangle to form frame profile ---
        frame_profile = outer_rect.rect(inner_length, inner_width, mode="s") if False else (
            cq.Workplane("XY")
            .rect(outer_length, outer_width)
            .extrude(height)
            .faces(">Z").workplane()
            .rect(inner_length, inner_width)
            .cutThruAll()
        )
    
        result = frame_profile
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - outer_length) < TOL, \
            f"X length: expected {outer_length}, got {bb.xlen}"
        assert abs(bb.ylen - outer_width) < TOL, \
            f"Y length: expected {outer_width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z height: expected {height}, got {bb.zlen}"
    
        # Bounding box extents centered at origin
        assert abs(bb.xmin - (-outer_length / 2)) < TOL, \
            f"xmin: expected {-outer_length/2}, got {bb.xmin}"
        assert abs(bb.xmax - ( outer_length / 2)) < TOL, \
            f"xmax: expected { outer_length/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-outer_width  / 2)) < TOL, \
            f"ymin: expected {-outer_width/2}, got {bb.ymin}"
        assert abs(bb.ymax - ( outer_width  / 2)) < TOL, \
            f"ymax: expected { outer_width/2}, got {bb.ymax}"
    
        # Volume check: frame area = outer_area - inner_area, times height
        outer_area = outer_length * outer_width
        inner_area = inner_length * inner_width
        expected_vol = (outer_area - inner_area) * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Face count: a frame (square tube) has:
        #   2 flat faces (top + bottom)
        #   4 outer side faces
        #   4 inner side faces
        #   = 10 planar faces total
        face_count = result.faces().size()
        assert face_count == 10, \
            f"Face count: expected 10, got {face_count}"
    
        # Check that a point inside the inner hole is NOT inside the solid
        inner_point = (0.0, 0.0, height / 2)   # center of the hole
        assert not result.val().isInside(inner_point), \
            f"Center point should be outside (in the hole), but isInside returned True"
    
        # Check that a point in the frame material IS inside the solid
        frame_point = (outer_length / 2 - padding / 2, 0.0, height / 2)
        assert result.val().isInside(frame_point), \
            f"Frame material point should be inside the solid, but isInside returned False"
    
        # Cylindrical faces: none expected (all planar)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 0, \
            f"Cylindrical faces: expected 0, got {cyl_face_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00038614/gpt_generated.stl')
