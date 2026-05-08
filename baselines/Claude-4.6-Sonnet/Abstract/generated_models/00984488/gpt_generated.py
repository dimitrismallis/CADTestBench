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
        side = 20.0       # square side length
        depth = 10.0      # extrusion depth
        r = side / 2      # semicircle radius = 10
    
        # --- Step 1: Draw the combined profile (square + semicircle on top) ---
        # Square corners: bottom-left(-10,0), bottom-right(10,0), top-right(10,20), top-left(-10,20)
        # Semicircle: from top-right(10,20) arcing through (0,30) to top-left(-10,20)
        # The midpoint of the arc (topmost point) is at (0, 20+r) = (0, 30)
    
        result = (
            cq.Workplane("XY")
            .moveTo(-side/2, 0)           # bottom-left
            .lineTo(side/2, 0)            # bottom-right
            .lineTo(side/2, side)         # top-right
            .threePointArc((0, side + r), (-side/2, side))  # semicircle arc through top
            .lineTo(-side/2, 0)           # back to bottom-left (close)
            .close()
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # X extents: -10 to +10 → xlen = 20
        assert abs(bb.xlen - side) < TOL, f"X length: expected {side}, got {bb.xlen}"
    
        # Y extents: 0 to 30 (square 20 + semicircle radius 10) → ylen = 30
        expected_ylen = side + r
        assert abs(bb.ylen - expected_ylen) < TOL, f"Y length: expected {expected_ylen}, got {bb.ylen}"
    
        # Z extents: 0 to 10 → zlen = 10
        assert abs(bb.zlen - depth) < TOL, f"Z length: expected {depth}, got {bb.zlen}"
    
        # Volume: (square area + semicircle area) * depth
        square_area = side * side                        # 400
        semicircle_area = 0.5 * math.pi * r * r         # 0.5 * pi * 100 ≈ 157.08
        expected_vol = (square_area + semicircle_area) * depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # The solid should have exactly 1 solid
        assert result.solids().size() == 1, f"Expected 1 solid, got {result.solids().size()}"
    
        # Face count:
        # 1. Bottom flat face (full profile at z=0)
        # 2. Top flat face (full profile at z=depth)
        # 3. Left rectangular face (left side of square)
        # 4. Right rectangular face (right side of square)
        # 5. Bottom rectangular face (bottom of square)
        # 6. Curved cylindrical face (semicircle arc extruded)
        # Total = 6 (the top edge of the square is interior to the profile, not a separate face)
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Should have exactly 1 cylindrical face (the curved semicircle surface)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check the top of the semicircle is at y = side + r = 30
        assert abs(bb.ymax - (side + r)) < TOL, f"Y max: expected {side + r}, got {bb.ymax}"
    
        # Check the bottom is at y = 0
        assert abs(bb.ymin - 0) < TOL, f"Y min: expected 0, got {bb.ymin}"
    
        # Check center of mass is on the XZ symmetry plane (x=0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
    
        # Center of mass Z should be at depth/2 = 5
        assert abs(com.z - depth/2) < TOL, f"Center of mass Z: expected {depth/2}, got {com.z}"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"  Faces: {face_count}, Cylindrical faces: {cyl_faces}")
        print(f"  Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00984488/gpt_generated.stl')
