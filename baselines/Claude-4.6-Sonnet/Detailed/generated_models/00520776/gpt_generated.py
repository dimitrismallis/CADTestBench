import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Draw outer circle and extrude to form the cylinder ---
        outer_radius = 1.5 / 2          # 0.75
        height       = 0.381001
        hole_radius  = 0.060198 / 2     # 0.030099
    
        result = (
            cq.Workplane("XY")
            .circle(outer_radius)
            .extrude(height)
        )
    
        # --- Step 2: Draw inner (hole) circle at center and negatively extrude (cut) through ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(hole_radius)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 1.5) < TOL,        f"X diameter: expected 1.5, got {bb.xlen}"
        assert abs(bb.ylen - 1.5) < TOL,        f"Y diameter: expected 1.5, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL,     f"Height: expected {height}, got {bb.zlen}"
    
        # Volume check: cylinder minus hole
        vol_outer = math.pi * (outer_radius ** 2) * height
        vol_hole  = math.pi * (hole_radius  ** 2) * height
        expected_vol = vol_outer - vol_hole
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-3, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 2 flat circular annular faces (top + bottom) + 1 outer cylindrical + 1 inner cylindrical = 4
        face_count = result.faces().size()
        assert face_count == 4, f"Face count: expected 4, got {face_count}"
    
        # Cylindrical faces: outer barrel + inner hole barrel = 2
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Planar faces: top annulus + bottom annulus = 2
        plane_face_count = result.faces("%Plane").size()
        assert plane_face_count == 2, f"Planar face count: expected 2, got {plane_face_count}"
    
        # Circular edges: top outer, top inner, bottom outer, bottom inner = 4
        circ_edge_count = result.edges("%Circle").size()
        assert circ_edge_count == 4, f"Circular edge count: expected 4, got {circ_edge_count}"
    
        # Verify hole exists: a point at the center axis mid-height should be OUTSIDE the solid
        mid_z = height / 2
        center_point = (0.0, 0.0, mid_z)
        assert not result.val().isInside(center_point), \
            f"Center of hole should be outside the solid (hole not created properly)"
    
        # Verify a point on the outer body (halfway between hole and outer wall) is INSIDE
        mid_r = (outer_radius + hole_radius) / 2
        body_point = (mid_r, 0.0, mid_z)
        assert result.val().isInside(body_point), \
            f"Point in body at r={mid_r:.4f} should be inside the solid"
    
        # Center of mass should be at (0, 0, height/2) due to symmetry
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, f"CoM Z: expected {height/2}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520776/gpt_generated.stl')
