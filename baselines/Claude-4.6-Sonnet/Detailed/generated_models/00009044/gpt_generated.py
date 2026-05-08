import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        height = 0.375
        diameter = 1.5
        radius = diameter / 2.0          # 0.75
        hole_diameter = 0.237219
        hole_radius = hole_diameter / 2.0  # ~0.1186095
    
        # --- Step 1: Create the main cylinder ---
        result = cq.Workplane("XY").cylinder(height, radius)
    
        # --- Step 2: Add central circular cutout (through-hole) ---
        result = result.faces(">Z").workplane().hole(hole_diameter)
    
        # --- Final object verification ---
        TOL = 1e-3
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - diameter) < TOL, f"X extent: expected {diameter}, got {bb.xlen}"
        assert abs(bb.ylen - diameter) < TOL, f"Y extent: expected {diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL,   f"Z extent: expected {height}, got {bb.zlen}"
    
        # Volume check: cylinder minus central hole
        outer_vol = math.pi * radius**2 * height
        hole_vol  = math.pi * hole_radius**2 * height
        expected_vol = outer_vol - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 
        # Outer cylindrical face (1) + inner cylindrical face (1) + top annular face (1) + bottom annular face (1) = 4
        face_count = result.faces().size()
        assert face_count == 4, f"Face count: expected 4, got {face_count}"
    
        # Cylindrical faces: outer wall + inner hole wall = 2
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Planar faces: top + bottom = 2
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, f"Planar face count: expected 2, got {planar_face_count}"
    
        # Circular edges: top outer, top inner, bottom outer, bottom inner = 4
        circ_edge_count = result.edges("%Circle").size()
        assert circ_edge_count == 4, f"Circular edge count: expected 4, got {circ_edge_count}"
    
        # Center of mass should be at origin (symmetric cylinder)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"CoM Z: expected 0, got {com.z}"
    
        # Verify hole exists: a point at the center axis inside the hole should NOT be inside the solid
        mid_z = 0.0  # center of cylinder height
        inside_hole = result.val().isInside((0, 0, mid_z))
        assert not inside_hole, "Center point should be inside the hole (not inside solid)"
    
        # Verify a point on the annular ring IS inside the solid
        mid_r = (radius + hole_radius) / 2.0
        inside_solid = result.val().isInside((mid_r, 0, mid_z))
        assert inside_solid, f"Point at r={mid_r} should be inside the solid annular region"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00009044/gpt_generated.stl')
