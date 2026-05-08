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
        outer_diameter = 100.0   # large diameter
        outer_radius   = outer_diameter / 2.0
        height         = 40.0    # height < diameter, so cylinder is wider than tall
        hole_diameter  = 10.0    # small central cutout
        hole_radius    = hole_diameter / 2.0
    
        # --- Step 1: Create the large base cylinder ---
        result = cq.Workplane("XY").cylinder(height, outer_radius)
    
        # --- Step 2: Cut a small circular hole through the center (full height) ---
        result = result.faces(">Z").workplane().hole(hole_diameter)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box: diameter 100 in X and Y, height 40 in Z
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - outer_diameter) < TOL, \
            f"X extent: expected {outer_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - outer_diameter) < TOL, \
            f"Y extent: expected {outer_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z extent: expected {height}, got {bb.zlen}"
    
        # Diameter must be greater than height
        assert outer_diameter > height, \
            f"Diameter {outer_diameter} should be greater than height {height}"
    
        # Check volume: large cylinder minus small central hole
        vol_outer = math.pi * outer_radius**2 * height
        vol_hole  = math.pi * hole_radius**2 * height
        expected_vol = vol_outer - vol_hole
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check cylindrical faces: outer cylinder wall + inner hole wall = 2 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2 (outer + inner), got {cyl_faces}"
    
        # Check planar faces: top and bottom flat faces = 2 planar faces
        # (each has an annular ring shape — still planar)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, \
            f"Planar faces: expected 2 (top + bottom annuli), got {planar_faces}"
    
        # Check circular edges: top outer, top inner, bottom outer, bottom inner = 4
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 4, \
            f"Circular edges: expected 4, got {circ_edges}"
    
        # Check the hole exists at center: a point at (0,0,0) should be OUTSIDE the solid
        # (it's inside the cutout)
        solid = result.val()
        center_point = (0.0, 0.0, 0.0)
        assert not solid.isInside(center_point), \
            "Center point (0,0,0) should be inside the hole cutout, not inside the solid"
    
        # Check a point on the solid body is inside (e.g., midway between hole and outer edge)
        mid_r = (outer_radius + hole_radius) / 2.0
        body_point = (mid_r, 0.0, 0.0)
        assert solid.isInside(body_point), \
            f"Point at radius {mid_r} should be inside the solid body"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00001490/gpt_generated.stl')
