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
        cyl_radius   = 20.0   # cylinder outer radius (mm)
        cyl_height   = 30.0   # cylinder height (mm)
        oct_diameter = 20.0   # octagon circumscribed circle diameter (mm) → radius = 10 mm
    
        # --- Step 1: Create the cylinder ---
        # Draw a circle on XY plane and extrude upward
        result = (
            cq.Workplane("XY")
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # --- Step 2: Create the octagonal hole ---
        # Select the top face, place a workplane, draw a regular octagon, cut through all
        result = (
            result
            .faces(">Z")
            .workplane()
            .polygon(8, oct_diameter)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 2a. Bounding box: should be 2*cyl_radius × 2*cyl_radius × cyl_height
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 2 * cyl_radius) < TOL, \
            f"BBox X: expected {2*cyl_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * cyl_radius) < TOL, \
            f"BBox Y: expected {2*cyl_radius}, got {bb.ylen}"
        assert abs(bb.zlen - cyl_height) < TOL, \
            f"BBox Z: expected {cyl_height}, got {bb.zlen}"
    
        # 2b. Volume: cylinder volume minus octagonal prism volume
        cyl_vol = math.pi * cyl_radius**2 * cyl_height
        # Regular octagon area with circumradius R = oct_diameter/2
        R_oct = oct_diameter / 2.0
        oct_area = 2.0 * math.sqrt(2) * R_oct**2
        oct_vol  = oct_area * cyl_height
        expected_vol = cyl_vol - oct_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 2c. Face count:
        #   - 1 cylindrical (outer) face
        #   - 1 top annular face (ring: circle minus octagon)
        #   - 1 bottom annular face (ring: circle minus octagon)
        #   - 8 rectangular inner faces (walls of the octagonal hole)
        #   Total = 11 faces
        face_count = result.faces().size()
        assert face_count == 11, \
            f"Face count: expected 11, got {face_count}"
    
        # 2d. Cylindrical face count: exactly 1 (outer cylinder wall)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 1, \
            f"Cylindrical faces: expected 1, got {cyl_face_count}"
    
        # 2e. Planar face count: 2 annular rings + 8 octagon walls = 10
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 10, \
            f"Planar faces: expected 10, got {planar_face_count}"
    
        # 2f. The object should have exactly 1 solid
        solid_count = result.solids().size()
        assert solid_count == 1, \
            f"Solid count: expected 1, got {solid_count}"
    
        # 2g. Center of mass should be at (0, 0, cyl_height/2) by symmetry
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - cyl_height / 2.0) < TOL, \
            f"CoM Z: expected {cyl_height/2.0}, got {com.z}"
    
        # 2h. A point at the center (0,0,15) should NOT be inside (it's the hole)
        center_point = (0.0, 0.0, cyl_height / 2.0)
        assert not result.val().isInside(center_point), \
            "Center point should be inside the octagonal hole (not inside solid)"
    
        # 2i. A point near the outer rim should be inside the solid
        outer_point = (cyl_radius * 0.85, 0.0, cyl_height / 2.0)
        assert result.val().isInside(outer_point), \
            f"Outer point {outer_point} should be inside the solid cylinder wall"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997536/gpt_generated.stl')
