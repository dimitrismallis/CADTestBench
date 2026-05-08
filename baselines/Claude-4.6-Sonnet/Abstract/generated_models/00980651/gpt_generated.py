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
        hex_circumradius = 20.0       # circumradius of hexagon (vertex to center)
        hex_height = 30.0             # extrusion height of hexagon
        hex_inradius = hex_circumradius * math.cos(math.radians(30))  # ~17.32mm
        cyl_radius = 15.0             # slightly smaller than inradius (~17.32mm)
        cyl_height = hex_height / 2   # half the hexagon height = 15mm
    
        # --- Step 1: Create hexagon base and extrude ---
        # polygon(6, diameter) where diameter = 2 * circumradius
        hex_diameter = 2 * hex_circumradius  # 40mm
        result = (
            cq.Workplane("XY")
            .polygon(6, hex_diameter)
            .extrude(hex_height)
        )
    
        # --- Step 2: Create cylinder on top of hexagon ---
        # Move workplane to top face of hexagon (z = hex_height)
        # then draw circle and extrude upward
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Overall bounding box checks
        bb = result.val().BoundingBox()
    
        # X and Y extents: hexagon dominates (circumradius=20 → xlen=40, ylen=40)
        # Hexagon with flat sides: xlen = 2*circumradius = 40, ylen = 2*inradius = ~34.64
        expected_xlen = 2 * hex_circumradius  # 40.0
        expected_ylen = 2 * hex_inradius      # ~34.64
        expected_zlen = hex_height + cyl_height  # 30 + 15 = 45
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"BBox X: expected {expected_xlen:.3f}, got {bb.xlen:.3f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"BBox Y: expected {expected_ylen:.3f}, got {bb.ylen:.3f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"BBox Z: expected {expected_zlen:.3f}, got {bb.zlen:.3f}"
    
        # Volume check
        # Hexagon volume: area of regular hexagon = (3*sqrt(3)/2) * r^2, r=circumradius
        hex_area = (3 * math.sqrt(3) / 2) * (hex_circumradius ** 2)
        hex_vol = hex_area * hex_height
        cyl_vol = math.pi * (cyl_radius ** 2) * cyl_height
        expected_vol = hex_vol + cyl_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count checks:
        # Hexagon prism: 6 side faces + 1 bottom + 1 top (but top is partially covered by cylinder base)
        # Cylinder: 1 curved face + 1 top circle
        # The interface between cylinder base and hex top creates a ring face on hex top
        # Expected faces: 6 (hex sides) + 1 (hex bottom) + 1 (hex top ring) + 1 (cyl curved) + 1 (cyl top) = 10
        face_count = result.faces().size()
        assert face_count == 10, \
            f"Face count: expected 10, got {face_count}"
    
        # Check cylindrical faces (cylinder curved surface = 1)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, \
            f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check planar faces (6 hex sides + 1 bottom + 1 hex top ring + 1 cyl top = 9)
        plane_faces = result.faces("%Plane").size()
        assert plane_faces == 9, \
            f"Planar faces: expected 9, got {plane_faces}"
    
        # Check top face is at z = hex_height + cyl_height = 45
        top_z = result.faces(">Z").val().Center().z
        assert abs(top_z - (hex_height + cyl_height)) < TOL, \
            f"Top face Z: expected {hex_height + cyl_height}, got {top_z}"
    
        # Check bottom face is at z = 0
        bot_z = result.faces("<Z").val().Center().z
        assert abs(bot_z - 0.0) < TOL, \
            f"Bottom face Z: expected 0.0, got {bot_z}"
    
        # Check center of mass is on Z axis (symmetric shape)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected ~0, got {com.y}"
    
        # Check cylinder is inside the hexagon footprint (point at cyl_radius-1 should be inside)
        test_point = (cyl_radius - 1, 0, hex_height + cyl_height / 2)
        assert result.val().isInside(test_point), \
            f"Point {test_point} should be inside the cylinder"
    
        # Check a point outside cylinder but inside hex at hex mid-height is inside solid
        test_point2 = (hex_inradius - 1, 0, hex_height / 2)
        assert result.val().isInside(test_point2), \
            f"Point {test_point2} should be inside the hexagon"
    
        # Check a point outside hex is NOT inside solid
        test_point3 = (hex_circumradius + 1, 0, hex_height / 2)
        assert not result.val().isInside(test_point3), \
            f"Point {test_point3} should be outside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00980651/gpt_generated.stl')
