import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create rectangle (length=0.42, width=0.75) and extrude by 0.015 ---
        result = (
            cq.Workplane("XY")
            .rect(0.42, 0.75)
            .extrude(0.015)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Check bounding box dimensions
        assert abs(bb.xlen - 0.42) < TOL, f"X length: expected 0.42, got {bb.xlen}"
        assert abs(bb.ylen - 0.75) < TOL, f"Y length: expected 0.75, got {bb.ylen}"
        assert abs(bb.zlen - 0.015) < TOL, f"Z length (extrusion): expected 0.015, got {bb.zlen}"
    
        # Check volume
        expected_volume = 0.42 * 0.75 * 0.015
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.001, \
            f"Volume: expected {expected_volume:.6f}, got {actual_volume:.6f}"
    
        # Check face count: a box has 6 faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Check that it is a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        # Check center of mass is at origin (centered box)
        center = cq.Shape.centerOfMass(result.val())
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z - 0.0075) < TOL, f"Center Z: expected 0.0075, got {center.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00006013/gpt_generated.stl')
