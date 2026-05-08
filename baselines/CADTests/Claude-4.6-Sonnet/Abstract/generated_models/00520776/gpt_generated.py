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
        outer_radius = 20.0      # mm
        hole_radius  = 1.0       # mm  (very small)
        height       = 30.0      # mm
    
        # --- Step 1: Outer cylinder — draw circle and extrude positively ---
        result = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .extrude(height)
        )
    
        # --- Step 2: Small hole — draw tiny circle on top face and cut through ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(hole_radius)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 2a. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 2 * outer_radius) < TOL, \
            f"X extent: expected {2*outer_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * outer_radius) < TOL, \
            f"Y extent: expected {2*outer_radius}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z extent: expected {height}, got {bb.zlen}"
    
        # 2b. Volume check: outer cylinder minus small hole cylinder
        outer_vol = math.pi * outer_radius**2 * height
        hole_vol  = math.pi * hole_radius**2  * height
        expected_vol = outer_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.4f}, got {actual_vol:.4f}"
    
        # 2c. Face count: 2 flat annular end-caps + 1 outer cylindrical face + 1 inner cylindrical face = 4
        face_count = result.faces().size()
        assert face_count == 4, \
            f"Face count: expected 4 (2 annular caps + outer cyl + inner cyl), got {face_count}"
    
        # 2d. Cylindrical faces: outer barrel + inner hole barrel = 2
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # 2e. Planar faces: top and bottom annular rings = 2
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, \
            f"Planar face count: expected 2, got {planar_face_count}"
    
        # 2f. Confirm hole exists: a point on the central axis inside the hole should NOT be inside the solid
        mid_z = height / 2.0
        point_in_hole = (0.0, 0.0, mid_z)   # dead center — inside the hole
        assert not result.val().isInside(point_in_hole), \
            f"Center point {point_in_hole} should be inside the hole (not solid), but isInside returned True"
    
        # 2g. Confirm material exists just outside the hole radius
        point_in_solid = (outer_radius / 2.0, 0.0, mid_z)
        assert result.val().isInside(point_in_solid), \
            f"Point {point_in_solid} should be inside the solid, but isInside returned False"
    
        # 2h. Circular edges: top outer + top inner + bottom outer + bottom inner = 4
        circ_edge_count = result.edges("%Circle").size()
        assert circ_edge_count == 4, \
            f"Circular edge count: expected 4, got {circ_edge_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520776/gpt_generated.stl')
