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
        # --- Parameters (converted to mm) ---
        outer_length = 60.0    # 0.06 m
        outer_width  = 60.0    # 0.06 m
        height       = 750.0   # 0.75 m
        padding      = 4.5     # 0.0045 m inside padding on all sides
    
        inner_length = outer_length - 2 * padding  # 51.0 mm
        inner_width  = outer_width  - 2 * padding  # 51.0 mm
    
        # --- Step 1: Create outer profile and subtract inner profile ---
        # Use Sketch API to create a rectangular annulus (hollow rectangle)
        profile = (
            cq.Workplane("XY")
            .rect(outer_length, outer_width)
            .rect(inner_length, inner_width)
        )
    
        # --- Step 2: Extrude the hollow profile to create the pipe ---
        result = (
            cq.Workplane("XY")
            .rect(outer_length, outer_width)
            .extrude(height)
            .faces(">Z")
            .workplane()
            .rect(inner_length, inner_width)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - outer_length) < TOL, f"X length: expected {outer_length}, got {bb.xlen}"
        assert abs(bb.ylen - outer_width)  < TOL, f"Y width:  expected {outer_width},  got {bb.ylen}"
        assert abs(bb.zlen - height)       < TOL, f"Z height: expected {height},       got {bb.zlen}"
    
        # Check volume: outer box minus inner hollow
        outer_vol = outer_length * outer_width * height
        inner_vol = inner_length * inner_width * height
        expected_vol = outer_vol - inner_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check that the pipe is hollow: a point in the center of the inner cavity should be outside
        center_point = (0, 0, height / 2)
        assert not result.val().isInside(center_point), \
            f"Center of pipe should be hollow (outside solid), but isInside returned True"
    
        # Check that a point in the wall is inside the solid
        wall_point = (outer_length / 2 - padding / 2, 0, height / 2)
        assert result.val().isInside(wall_point), \
            f"Wall point {wall_point} should be inside the solid, but isInside returned False"
    
        # Check cylindrical faces (none expected — all faces should be planar)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Check face count: 
        # Outer: 4 side faces + top ring + bottom ring = 6 outer faces
        # Inner: 4 inner side faces
        # Total planar faces = 4 (outer sides) + 4 (inner sides) + 2 (top/bottom rings) = 10
        face_count = result.faces().size()
        assert face_count == 10, f"Expected 10 planar faces, got {face_count}"
    
        # Check that the pipe has exactly 1 solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Expected 1 solid, got {solid_count}"
    
        # Verify center of mass is at the geometric center
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, f"Center of mass Z: expected {height/2}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670259/gpt_generated.stl')
