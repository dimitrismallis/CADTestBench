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
        length = 0.75
        width  = 0.1875
        height = 0.00391
        hole_diameter = 0.12512
        hole_radius   = hole_diameter / 2.0  # 0.06256
    
        # --- Step 1: Create the rectangular block ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Add a circular through-hole at the center ---
        result = result.faces(">Z").workplane().hole(hole_diameter)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Check volume: block volume minus cylinder volume
        block_vol    = length * width * height
        hole_vol     = math.pi * hole_radius**2 * height
        expected_vol = block_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Check that there is exactly one cylindrical face (the hole wall)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check planar faces: 6 for a box (top, bottom, 4 sides), hole openings are inner wires
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 6, f"Planar faces: expected 6, got {planar_faces}"
    
        # Check circular edges: 2 (top and bottom circles of the hole)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 2, f"Circular edges: expected 2, got {circ_edges}"
    
        # Check center of mass is at origin (symmetric block centered at origin)
        # box() centers at origin, so Z center of mass = 0
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected 0, got {com.z}"
    
        # Check hole is present: a point at the center (inside the hole) should NOT be inside the solid
        center_point = (0, 0, 0)
        assert not result.val().isInside(center_point), \
            "Center point should be inside the hole (not inside the solid)"
    
        # Check a point well within the solid (away from hole) IS inside
        solid_point = (length/2 - 0.05, 0, 0)
        assert result.val().isInside(solid_point), \
            f"Point {solid_point} should be inside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00000633/gpt_generated.stl')
