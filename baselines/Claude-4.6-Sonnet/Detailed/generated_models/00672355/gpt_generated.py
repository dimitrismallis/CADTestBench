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
        cyl_diameter = 0.95
        cyl_radius   = cyl_diameter / 2.0   # 0.475
        cyl_height   = 0.475
    
        rect_width   = 0.76    # ~4/5 of diameter
        rect_length  = 0.7
        rect_extrude = 0.2375  # ~half the cylinder height
    
        # --- Step 1: Base cylinder ---
        # Draw circle of diameter 0.95, extrude to height 0.475
        result = (
            cq.Workplane("XY")
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # --- Step 2: Rectangular protrusion on top face ---
        # Center a rectangle (0.76 wide x 0.7 long) on the top face,
        # then extrude upward by 0.2375
        result = (
            result
            .faces(">Z")
            .workplane()
            .rect(rect_width, rect_length)
            .extrude(rect_extrude)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: cylinder diameter = 0.95
        assert abs(bb.xlen - cyl_diameter) < TOL, \
            f"X extent: expected {cyl_diameter}, got {bb.xlen}"
    
        # Y extent: cylinder diameter = 0.95
        assert abs(bb.ylen - cyl_diameter) < TOL, \
            f"Y extent: expected {cyl_diameter}, got {bb.ylen}"
    
        # Z extent: cylinder height + rect extrusion = 0.475 + 0.2375 = 0.7125
        expected_zlen = cyl_height + rect_extrude
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z extent: expected {expected_zlen}, got {bb.zlen}"
    
        # Z min should be 0 (base at XY plane)
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
    
        # Z max should be cyl_height + rect_extrude
        assert abs(bb.zmax - expected_zlen) < TOL, \
            f"Z max: expected {expected_zlen}, got {bb.zmax}"
    
        # Volume check:
        # Cylinder volume = pi * r^2 * h
        cyl_vol = math.pi * (cyl_radius ** 2) * cyl_height
        # Rectangular box volume = width * length * extrude_height
        rect_vol = rect_width * rect_length * rect_extrude
        expected_vol = cyl_vol + rect_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: OCCT splits the annular top region and rectangle sides
        # at intersections with the cylinder boundary, resulting in 15 faces total
        face_count = result.faces().size()
        assert face_count == 15, \
            f"Face count: expected 15, got {face_count}"
    
        # Check cylindrical face exists (the cylinder side)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Cylindrical faces: expected at least 1, got {cyl_faces}"
    
        # Check the top face is at the correct Z height
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - expected_zlen) < TOL, \
            f"Top face Z center: expected {expected_zlen}, got {top_face_z}"
    
        # Check bottom face is at Z=0
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z - 0.0) < TOL, \
            f"Bottom face Z center: expected 0.0, got {bot_face_z}"
    
        # Check center of mass is on Z axis (x=0, y=0) due to symmetry
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
    
        # Verify the rectangular protrusion dimensions via bounding box of top face
        top_face = result.faces(">Z").val()
        top_bb = top_face.BoundingBox()
        assert abs(top_bb.xlen - rect_width) < TOL, \
            f"Top face X width: expected {rect_width}, got {top_bb.xlen}"
        assert abs(top_bb.ylen - rect_length) < TOL, \
            f"Top face Y length: expected {rect_length}, got {top_bb.ylen}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00672355/gpt_generated.stl')
