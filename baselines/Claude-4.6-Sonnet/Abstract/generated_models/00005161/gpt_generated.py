import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        big_r = 30       # big cylinder radius
        big_h = 40       # big cylinder height
        small_r = 25     # small cylinder radius (slightly smaller)
        small_h = 60     # small cylinder height (larger than big)
    
        # --- Step 1: Create the big cylinder centered at origin ---
        # Spans z = -big_h/2 to z = +big_h/2 = -20 to +20
        big_cyl = cq.Workplane("XY").cylinder(big_h, big_r)
    
        # --- Step 2: Create the small cylinder connected to the center of the big cylinder's base ---
        # The base (bottom) of the big cylinder is at z = -big_h/2 = -20
        # The small cylinder extends downward from z = -20 to z = -20 - small_h = -80
        # Place it centered at z = -20 - small_h/2 = -50
        small_cyl_center_z = -big_h / 2 - small_h / 2  # = -20 - 30 = -50
        small_cyl = cq.Workplane("XY", origin=(0, 0, small_cyl_center_z)).cylinder(small_h, small_r)
    
        # --- Step 3: Union both cylinders ---
        result = big_cyl.union(small_cyl)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X and Y extents should be dominated by the big cylinder (radius=30 → diameter=60)
        assert abs(bb.xlen - 2 * big_r) < TOL, f"X extent: expected {2*big_r}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * big_r) < TOL, f"Y extent: expected {2*big_r}, got {bb.ylen}"
    
        # Z extents: top of big cylinder at +20, bottom of small cylinder at -80
        expected_zmax = big_h / 2                        # +20
        expected_zmin = -(big_h / 2 + small_h)           # -80
        expected_zlen = big_h + small_h                  # 40 + 60 = 100
        assert abs(bb.zmax - expected_zmax) < TOL, f"Z max: expected {expected_zmax}, got {bb.zmax}"
        assert abs(bb.zmin - expected_zmin) < TOL, f"Z min: expected {expected_zmin}, got {bb.zmin}"
        assert abs(bb.zlen - expected_zlen) < TOL, f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check: sum of both cylinders (they share only a circle at z=-20, no overlap volume)
        vol_big = math.pi * big_r**2 * big_h
        vol_small = math.pi * small_r**2 * small_h
        expected_vol = vol_big + vol_small
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count analysis after union of two cylinders with different radii:
        # Since big_r (30) > small_r (25), at z=-20 the junction:
        #   - Big cylinder bottom: annular ring from r=25 to r=30 (exposed, remains as a face)
        #   - Small cylinder top: circle r=25 (internal, removed by union)
        # Resulting faces:
        #   1. Big cylinder top flat cap (circle r=30) at z=+20
        #   2. Big cylinder curved side surface
        #   3. Big cylinder bottom annular ring (r=25..30) at z=-20  ← exposed step
        #   4. Small cylinder curved side surface
        #   5. Small cylinder bottom flat cap (circle r=25) at z=-80
        # Total = 5 faces
        face_count = result.faces().size()
        assert face_count == 5, f"Face count: expected 5, got {face_count}"
    
        # Cylindrical faces: 2 (one for each cylinder's curved surface)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, f"Cylindrical faces: expected 2, got {cyl_face_count}"
    
        # Planar faces: 3 (top cap of big cyl, annular ring at junction, bottom cap of small cyl)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 3, f"Planar faces: expected 3, got {planar_face_count}"
    
        # Top face at z = +20 (big cylinder top)
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - expected_zmax) < TOL, f"Top face Z: expected {expected_zmax}, got {top_face_z}"
    
        # Bottom face at z = -80 (small cylinder bottom)
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z - expected_zmin) < TOL, f"Bottom face Z: expected {expected_zmin}, got {bot_face_z}"
    
        # Center of mass should be on the Z axis (x=0, y=0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
    
        # The big cylinder's top is wider — verify a point inside big cyl but outside small cyl
        # Point at (28, 0, 0) should be inside (within big cylinder radius=30)
        assert result.val().isInside((28, 0, 0)), "Point (28,0,0) should be inside big cylinder"
        # Point at (28, 0, -50) should be outside (outside small cylinder radius=25)
        assert not result.val().isInside((28, 0, -50)), "Point (28,0,-50) should be outside small cylinder"
        # Point at (20, 0, -50) should be inside (within small cylinder radius=25)
        assert result.val().isInside((20, 0, -50)), "Point (20,0,-50) should be inside small cylinder"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00005161/gpt_generated.stl')
