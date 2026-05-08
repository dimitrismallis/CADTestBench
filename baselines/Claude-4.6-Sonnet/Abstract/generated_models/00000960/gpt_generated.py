import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        rect1_w = 60.0   # width in X
        rect1_d = 10.0   # depth in Y
        rect1_h = 40.0   # height in Z
    
        rect2_w = 30.0   # width in X
        rect2_d = 10.0   # depth in Y
        rect2_h = 20.0   # height in Z
    
        # --- Step 1: Create the first (larger) rectangle as a box ---
        # centered in X and Y, starting at Z=0
        rect1 = cq.Workplane("XY").box(rect1_w, rect1_d, rect1_h, centered=(True, True, False))
    
        # --- Step 2: Create the second (smaller) rectangle ---
        # Connects to the RIGHT edge of rect1 (X = +30), starting HALFWAY UP (Z = 20)
        # rect2 spans: X: 30 to 60, Y: -5 to 5, Z: 20 to 40
        rect2_cx = rect1_w / 2 + rect2_w / 2   # center X = 45
        rect2_cz = rect1_h / 2                  # bottom of rect2 at Z=20
    
        rect2 = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(rect2_cx, 0, rect2_cz))
            .box(rect2_w, rect2_d, rect2_h, centered=(True, True, False))
        )
    
        # --- Step 3: Union the two boxes ---
        result = rect1.union(rect2)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Overall bounding box:
        # X: -30 to 60  → xlen = 90
        # Y: -5 to 5    → ylen = 10
        # Z: 0 to 40    → zlen = 40
        bb = result.val().BoundingBox()
    
        assert abs(bb.xlen - 90.0) < TOL, f"X length: expected 90.0, got {bb.xlen}"
        assert abs(bb.ylen - rect1_d) < TOL, f"Y length: expected {rect1_d}, got {bb.ylen}"
        assert abs(bb.zlen - rect1_h) < TOL, f"Z length: expected {rect1_h}, got {bb.zlen}"
    
        assert abs(bb.xmin - (-rect1_w / 2)) < TOL, f"xmin: expected {-rect1_w/2}, got {bb.xmin}"
        assert abs(bb.xmax - (rect1_w / 2 + rect2_w)) < TOL, f"xmax: expected {rect1_w/2 + rect2_w}, got {bb.xmax}"
        assert abs(bb.zmin - 0.0) < TOL, f"zmin: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - rect1_h) < TOL, f"zmax: expected {rect1_h}, got {bb.zmax}"
    
        # Volume check:
        # rect1 = 60 * 10 * 40 = 24000
        # rect2 = 30 * 10 * 20 = 6000
        # They share only a face (zero volume overlap)
        vol_rect1 = rect1_w * rect1_d * rect1_h   # 24000
        vol_rect2 = rect2_w * rect2_d * rect2_h   # 6000
        expected_vol = vol_rect1 + vol_rect2       # 30000
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Face count analysis for the L-shaped solid:
        # - Bottom face (Z=0, full rect1 width): 1
        # - Top face (Z=40, coplanar across both boxes, merged): 1
        # - Step face horizontal (Z=20, X=30..60, exposed bottom of rect2): 1
        # - Step face vertical (X=30, Z=0..20, right side of rect1 lower): 1
        # - Left face (X=-30): 1
        # - Right face (X=60): 1
        # - Front face (Y=-5, coplanar, merged): 1
        # - Back face (Y=+5, coplanar, merged): 1
        # Total = 8 planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 8, f"Planar face count: expected 8, got {planar_faces}"
    
        # Containment checks
        solid = result.val()
        # Inside rect1 lower half
        assert solid.isInside((0, 0, 10)), "Point (0,0,10) should be inside rect1 lower half"
        # Inside rect1 upper half
        assert solid.isInside((0, 0, 30)), "Point (0,0,30) should be inside rect1 upper half"
        # Inside rect2
        assert solid.isInside((45, 0, 30)), "Point (45,0,30) should be inside rect2"
        # Outside: right side, lower half (below rect2)
        assert not solid.isInside((45, 0, 10)), "Point (45,0,10) should be OUTSIDE (below rect2)"
        # Outside: far right beyond rect2
        assert not solid.isInside((65, 0, 30)), "Point (65,0,30) should be OUTSIDE (beyond rect2)"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00000960/gpt_generated.stl')
