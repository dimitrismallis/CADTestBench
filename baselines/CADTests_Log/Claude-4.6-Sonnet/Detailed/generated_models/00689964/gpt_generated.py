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
        hex_side = 0.61859          # hexagon side length
        head_height = 0.214286      # extrusion height of hex head
        bolt_diameter = 0.321427    # diameter of cylindrical shaft
        bolt_radius = bolt_diameter / 2.0
        bolt_height = 0.75025       # extrusion height of bolt shaft
    
        # --- Step 1: Draw hexagon and extrude upward to form the head ---
        # CadQuery's polygon(nSides, diameter) uses the circumscribed circle diameter
        # For a regular hexagon, circumradius = side length, so diameter = 2 * side
        hex_circumdiameter = 2 * hex_side  # = 2 * 0.61859 = 1.23718
    
        hex_head = (
            cq.Workplane("XY")
            .polygon(6, hex_circumdiameter)
            .extrude(head_height)
        )
    
        # --- Step 2: Draw circle on the bottom face and extrude downward for the bolt shaft ---
        # The bolt shaft extends downward (in -Z direction) from the bottom of the head
        result = (
            hex_head
            .faces("<Z")
            .workplane()
            .circle(bolt_radius)
            .extrude(bolt_height)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
    
        # Total height: head (0.214286) + shaft (0.75025) = 0.964536
        total_height = head_height + bolt_height
        assert abs(bb.zlen - total_height) < TOL, \
            f"Total Z height: expected {total_height:.6f}, got {bb.zlen:.6f}"
    
        # For a regular hexagon with side s, oriented with a flat vertex along X:
        # X bounding box = 2 * s (vertex to vertex) = circumdiameter
        # Y bounding box = s * sqrt(3) (flat to flat)
        hex_bb_x = hex_circumdiameter          # 1.23718
        hex_bb_y = hex_side * math.sqrt(3)    # 1.07143
    
        assert abs(bb.xlen - hex_bb_x) < TOL, \
            f"Bounding box X: expected {hex_bb_x:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - hex_bb_y) < TOL, \
            f"Bounding box Y: expected {hex_bb_y:.6f}, got {bb.ylen:.6f}"
    
        # Z extents: from -bolt_height to +head_height
        assert abs(bb.zmin - (-bolt_height)) < TOL, \
            f"Z min: expected {-bolt_height:.6f}, got {bb.zmin:.6f}"
        assert abs(bb.zmax - head_height) < TOL, \
            f"Z max: expected {head_height:.6f}, got {bb.zmax:.6f}"
    
        # Volume check:
        # Hex head volume: area of regular hexagon * height
        # Area of regular hexagon with side s = (3*sqrt(3)/2) * s^2
        hex_area = (3 * math.sqrt(3) / 2) * hex_side ** 2
        hex_vol = hex_area * head_height
    
        # Bolt shaft volume: pi * r^2 * h
        bolt_vol = math.pi * bolt_radius ** 2 * bolt_height
    
        expected_vol = hex_vol + bolt_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count check:
        # Hex head: 1 top face (hex), 6 side faces, 1 bottom annular face (hex with circle hole) = 8
        # Bolt shaft: 1 cylindrical face, 1 bottom circle face = 2
        # Total expected faces: 10
        face_count = result.faces().size()
        assert face_count == 10, \
            f"Face count: expected 10, got {face_count}"
    
        # Check cylindrical faces (bolt shaft lateral surface)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, \
            f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check that the top face is at max Z (hex head top)
        top_faces = result.faces(">Z").size()
        assert top_faces == 1, \
            f"Top face count: expected 1, got {top_faces}"
    
        # Check center of mass is roughly on Z axis (x~0, y~0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x:.6f}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y:.6f}"
    
        # Check the bolt shaft bottom face is at z = -bolt_height
        bottom_face_z = result.faces("<Z").val().Center().z
        assert abs(bottom_face_z - (-bolt_height)) < TOL, \
            f"Bottom face Z center: expected {-bolt_height:.6f}, got {bottom_face_z:.6f}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00689964/gpt_generated.stl')
