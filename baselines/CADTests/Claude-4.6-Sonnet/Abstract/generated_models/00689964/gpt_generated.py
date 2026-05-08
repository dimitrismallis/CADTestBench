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
        hex_circumradius = 6.93   # circumradius of hexagon (vertex-to-center)
        hex_height       = 4.0    # height of hexagonal head
        shaft_radius     = 4.0    # radius of cylindrical shaft
        shaft_length     = 20.0   # length of shaft below the head
    
        # --- Step 1: Draw hexagonal head ---
        # polygon(6, diameter) creates a hexagon with given circumdiameter
        # With a vertex pointing along X: xlen = 2*circumradius, ylen = sqrt(3)*circumradius
        hex_head = (
            cq.Workplane("XY")
            .polygon(6, hex_circumradius * 2)   # polygon(nSides, diameter)
            .extrude(hex_height)
        )
    
        # --- Step 2: Draw cylindrical shaft ---
        # Draw a circle on the XY plane (z=0) and extrude downward
        shaft = (
            cq.Workplane("XY")
            .circle(shaft_radius)
            .extrude(shaft_length, combine=False)
            .translate((0, 0, -shaft_length))
        )
    
        # --- Step 3: Union hex head and shaft ---
        result = hex_head.union(shaft)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # Total height = hex_height + shaft_length = 4 + 20 = 24
        expected_total_height = hex_height + shaft_length
        assert abs(bb.zlen - expected_total_height) < TOL, \
            f"Total Z height: expected {expected_total_height}, got {bb.zlen}"
    
        # Z extents: hex head from z=0 to z=hex_height, shaft from z=-shaft_length to z=0
        assert abs(bb.zmin - (-shaft_length)) < TOL, \
            f"Z min: expected {-shaft_length}, got {bb.zmin}"
        assert abs(bb.zmax - hex_height) < TOL, \
            f"Z max: expected {hex_height}, got {bb.zmax}"
    
        # X and Y extents of the hex head:
        # polygon(6, diameter) with default orientation has a vertex along X:
        #   xlen = 2 * circumradius (vertex to vertex)
        #   ylen = sqrt(3) * circumradius (flat to flat)
        expected_x_width = hex_circumradius * 2                  # ~13.86
        expected_y_width = hex_circumradius * math.sqrt(3)       # ~12.00
        assert abs(bb.xlen - expected_x_width) < TOL, \
            f"X width: expected ~{expected_x_width:.2f}, got {bb.xlen:.2f}"
        assert abs(bb.ylen - expected_y_width) < TOL, \
            f"Y width: expected ~{expected_y_width:.2f}, got {bb.ylen:.2f}"
    
        # Volume check
        # Hex area = (3*sqrt(3)/2) * r^2 where r is circumradius
        hex_area = (3 * math.sqrt(3) / 2) * (hex_circumradius ** 2)
        hex_vol  = hex_area * hex_height
        shaft_vol = math.pi * (shaft_radius ** 2) * shaft_length
        expected_vol = hex_vol + shaft_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count checks:
        # Hex head: 6 side faces + 1 top face + 1 annular bottom (hex minus shaft circle)
        # Shaft: 1 cylindrical face + 1 bottom circle face
        # Total expected: 10 faces
        total_faces = result.faces().size()
        assert total_faces >= 9, \
            f"Expected at least 9 faces, got {total_faces}"
    
        # Check cylindrical face exists (shaft)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, \
            f"Expected 1 cylindrical face (shaft), got {cyl_faces}"
    
        # Check top face is planar and at correct Z
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - hex_height) < TOL, \
            f"Top face Z center: expected {hex_height}, got {top_face_z}"
    
        # Check bottom face is at correct Z
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z - (-shaft_length)) < TOL, \
            f"Bottom face Z center: expected {-shaft_length}, got {bot_face_z}"
    
        # Check center of mass is on Z axis (symmetric)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y}"
    
        # COM should be between zmin and zmax
        assert bb.zmin < com.z < bb.zmax, \
            f"Center of mass Z ({com.z:.2f}) should be between {bb.zmin} and {bb.zmax}"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: X={bb.xlen:.2f}, Y={bb.ylen:.2f}, Z={bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected ~{expected_vol:.2f})")
        print(f"  Faces: {total_faces}, Cylindrical faces: {cyl_faces}")
        print(f"  Center of mass: ({com.x:.3f}, {com.y:.3f}, {com.z:.3f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00689964/gpt_generated.stl')
