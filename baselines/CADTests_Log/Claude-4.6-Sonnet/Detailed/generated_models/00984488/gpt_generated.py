import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        side = 0.86802
        r = side / 2.0          # 0.43401
        h = 0.152284
    
        # The square is centered at origin: X in [-r, r], Y in [-r, r]
        # Semi-circle sits on top edge (Y = r), arc goes up to Y = r + r = side
    
        # Build the closed profile as a wire using lineTo and threePointArc
        # Start at bottom-left corner, go clockwise around square, then arc over top
        profile = (
            cq.Workplane("XY")
            .moveTo(-r, -r)
            .lineTo(r, -r)
            .lineTo(r, r)
            # Semi-circle arc: from (r, r) through (0, r+r) to (-r, r)
            .threePointArc((0, r + r), (-r, r))
            .lineTo(-r, -r)
            .close()
        )
    
        # Extrude the profile
        result = profile.extrude(h)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # X extents: from -r to +r = side
        assert abs(bb.xlen - side) < TOL, f"X length: expected {side}, got {bb.xlen}"
    
        # Y extents: from -r to +(r+r) = from -0.43401 to 0.86802, total = side + r = 1.30203
        expected_ylen = side + r  # 0.86802 + 0.43401 = 1.30203
        assert abs(bb.ylen - expected_ylen) < TOL, f"Y length: expected {expected_ylen}, got {bb.ylen}"
    
        # Z extents: 0 to h
        assert abs(bb.zlen - h) < TOL, f"Z length: expected {h}, got {bb.zlen}"
    
        # Z min should be 0, Z max should be h
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - h) < TOL, f"Z max: expected {h}, got {bb.zmax}"
    
        # Volume: (square area + semi-circle area) * height
        square_area = side * side
        semicircle_area = math.pi * r * r / 2.0
        expected_vol = (square_area + semicircle_area) * h
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check face count: bottom face, top face (same profile), 
        # 3 rectangular side faces (left, right, bottom), 1 curved side face = 6 faces total
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Check cylindrical face exists (the curved side from semi-circle)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check planar faces: 5 (top, bottom, left, right, bottom-of-square side)
        plane_faces = result.faces("%Plane").size()
        assert plane_faces == 5, f"Planar faces: expected 5, got {plane_faces}"
    
        # Check the center of mass is at X=0 (symmetric about X axis)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00984488/gpt_generated.stl')
