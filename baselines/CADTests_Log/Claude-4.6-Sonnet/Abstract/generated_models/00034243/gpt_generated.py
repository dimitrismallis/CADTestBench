import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        disk_radius    = 30.0   # mm
        disk_height    = 10.0   # mm
        hole_diameter  = 6.0    # mm
        hole_spacing   = 20.0   # mm  (half-distance from center to hole center)
    
        # --- Step 1: Create the base circle and extrude into a disk/cylinder ---
        result = (
            cq.Workplane("XY")
            .circle(disk_radius)
            .extrude(disk_height)
        )
    
        # --- Step 2: Select the top face and create four holes in a square pattern ---
        # Holes are placed at (±hole_spacing, ±hole_spacing) relative to center
        result = (
            result
            .faces(">Z")
            .workplane()
            .rect(hole_spacing * 2, hole_spacing * 2, forConstruction=True)
            .vertices()
            .hole(hole_diameter)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box: diameter = 60mm in X and Y, height = 10mm in Z
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - disk_radius * 2) < TOL, \
            f"X extent: expected {disk_radius * 2}, got {bb.xlen}"
        assert abs(bb.ylen - disk_radius * 2) < TOL, \
            f"Y extent: expected {disk_radius * 2}, got {bb.ylen}"
        assert abs(bb.zlen - disk_height) < TOL, \
            f"Z extent: expected {disk_height}, got {bb.zlen}"
    
        # 2. Volume: disk volume minus four cylindrical holes
        disk_vol     = math.pi * disk_radius**2 * disk_height
        hole_vol     = 4 * math.pi * (hole_diameter / 2)**2 * disk_height
        expected_vol = disk_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical faces: OCCT produces 8 cylindrical faces
        #    (outer cylinder wall split into 4 arc segments + 4 hole cylinder walls)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 8, \
            f"Cylindrical faces: expected 8 (4 outer arc segments + 4 hole walls), got {cyl_faces}"
    
        # 4. Planar faces: top and bottom faces each split into multiple regions by the 4 holes
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 2, \
            f"Planar faces: expected at least 2 (top + bottom regions), got {planar_faces}"
    
        # 5. Circular edges: OCCT produces 16 circular/arc edges
        #    - Outer rim top arc × 4 + outer rim bottom arc × 4 = 8  (rim split by hole booleans)
        #    - Hole top circle × 4 + hole bottom circle × 4         = 8
        #    Total = 16
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 16, \
            f"Circular edges: expected 16, got {circ_edges}"
    
        # 6. Center of mass should be at (0, 0, disk_height/2) due to symmetry
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - disk_height / 2) < TOL, \
            f"CoM Z: expected {disk_height / 2}, got {com.z}"
    
        # 7. Verify holes pass through the solid (points at hole centers should be outside solid)
        solid = result.val()
        for sx, sy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            hole_center = (sx * hole_spacing, sy * hole_spacing, disk_height / 2)
            assert not solid.isInside(hole_center), \
                f"Point {hole_center} should be inside a hole (outside solid), but isInside returned True"
    
        # 8. Verify the solid center point IS inside the solid
        assert solid.isInside((0, 0, disk_height / 2)), \
            "Center of disk should be inside the solid"
    
        # 9. Verify points well inside the disk body (between holes) are inside the solid
        assert solid.isInside((0, 0, disk_height / 2)), \
            "Origin center should be inside the solid"
        assert solid.isInside((disk_radius * 0.5, 0, disk_height / 2)), \
            "Point halfway to rim along X should be inside the solid"
    
        # 10. Verify points outside the disk are outside the solid
        assert not solid.isInside((disk_radius + 5, 0, disk_height / 2)), \
            "Point outside disk radius should not be inside the solid"
        assert not solid.isInside((0, 0, disk_height + 5)), \
            "Point above disk should not be inside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00034243/gpt_generated.stl')
