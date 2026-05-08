import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create a rectangular prism centered at the origin ---
        length = 0.75
        width  = 0.0075
        height = 0.075
    
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Final object verification ---
        TOL = 1e-6
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Center at origin
        assert abs(bb.xmin + bb.xmax) < TOL, f"X center not at 0: xmin={bb.xmin}, xmax={bb.xmax}"
        assert abs(bb.ymin + bb.ymax) < TOL, f"Y center not at 0: ymin={bb.ymin}, ymax={bb.ymax}"
        assert abs(bb.zmin + bb.zmax) < TOL, f"Z center not at 0: zmin={bb.zmin}, zmax={bb.zmax}"
    
        # Volume check
        expected_vol = length * width * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-5, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # A rectangular prism has exactly 6 planar faces
        face_count = result.faces("%Plane").size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Center of mass should be at origin
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X not at 0: {com.x}"
        assert abs(com.y) < TOL, f"CoM Y not at 0: {com.y}"
        assert abs(com.z) < TOL, f"CoM Z not at 0: {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00008315/gpt_generated.stl')
