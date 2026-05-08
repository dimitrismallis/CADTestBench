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
        outer_diameter = 1.5
        outer_radius   = outer_diameter / 2.0       # 0.75
        height         = 0.113636
        hole_diameter  = 0.738636
        hole_radius    = hole_diameter / 2.0         # 0.369318
    
        # --- Step 1: Draw a circle of diameter 1.5 and extrude to height 0.113636 ---
        result = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .extrude(height)
        )
    
        # --- Step 2: Create a through-hole at the center with diameter 0.738636 ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .hole(hole_diameter)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - outer_diameter) < TOL, \
            f"X extent: expected {outer_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - outer_diameter) < TOL, \
            f"Y extent: expected {outer_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z extent (height): expected {height}, got {bb.zlen}"
    
        # Volume check: annular cylinder volume = pi * (R_outer^2 - R_inner^2) * h
        expected_vol = math.pi * (outer_radius**2 - hole_radius**2) * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: hollow cylinder has 4 faces:
        #   1 top annular face, 1 bottom annular face,
        #   1 outer cylindrical face, 1 inner cylindrical face
        face_count = result.faces().size()
        assert face_count == 4, \
            f"Face count: expected 4, got {face_count}"
    
        # Cylindrical faces: outer wall + inner wall = 2
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Planar faces: top + bottom = 2
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, \
            f"Planar face count: expected 2, got {planar_face_count}"
    
        # Circular edges: top outer, top inner, bottom outer, bottom inner = 4
        circ_edge_count = result.edges("%Circle").size()
        assert circ_edge_count == 4, \
            f"Circular edge count: expected 4, got {circ_edge_count}"
    
        # Check the hole is present: center of the cylinder should be empty (inside the hole)
        center_point = (0.0, 0.0, height / 2.0)
        is_inside = result.val().isInside(center_point)
        assert not is_inside, \
            f"Center point should be inside the hole (empty), but isInside returned True"
    
        # Check a point on the solid annular region is inside
        mid_radius = (outer_radius + hole_radius) / 2.0
        solid_point = (mid_radius, 0.0, height / 2.0)
        is_solid = result.val().isInside(solid_point)
        assert is_solid, \
            f"Point at mid-radius {mid_radius:.4f} should be inside the solid, but isInside returned False"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670817/gpt_generated.stl')
