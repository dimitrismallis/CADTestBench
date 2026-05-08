import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length   = 1.23418
        width    = 0.617188
        height   = 0.75
        cyl_h    = 0.140625
        cyl_d    = 0.380469
        cyl_r    = cyl_d / 2.0        # 0.190234
        padding  = 0.118359
    
        # --- Step 1: Base rectangular prism centered at origin ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Compute cylinder positions ---
        # Cylinders are symmetric along the length (X axis)
        # Each cylinder center is inset from the edge by padding + radius
        cx = length / 2.0 - padding - cyl_r   # 0.61709 - 0.118359 - 0.190234 ≈ 0.308497
        cy = 0.0                               # centered on width
        # Cylinders sit on top of the prism: bottom of cylinder at z = height/2
        cz_bottom = height / 2.0              # 0.375
        cz_center = cz_bottom + cyl_h / 2.0  # center of cylinder height
    
        # --- Step 3: Add two cylinders on top of the prism ---
        # Cylinder 1: positive X side
        cyl1 = (
            cq.Workplane("XY")
            .center(cx, cy)
            .workplane(offset=cz_center)
            .circle(cyl_r)
            .extrude(cyl_h / 2.0, both=True)
        )
    
        # Cylinder 2: negative X side
        cyl2 = (
            cq.Workplane("XY")
            .center(-cx, cy)
            .workplane(offset=cz_center)
            .circle(cyl_r)
            .extrude(cyl_h / 2.0, both=True)
        )
    
        result = result.union(cyl1).union(cyl2)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        expected_xlen = length
        expected_ylen = width
        expected_zlen = height + cyl_h  # prism height + cylinder height on top
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.5f}, got {bb.xlen:.5f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.5f}, got {bb.ylen:.5f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.5f}, got {bb.zlen:.5f}"
    
        # Z extents: prism bottom at -height/2, cylinder top at height/2 + cyl_h
        assert abs(bb.zmin - (-height / 2.0)) < TOL, \
            f"Z min: expected {-height/2.0:.5f}, got {bb.zmin:.5f}"
        assert abs(bb.zmax - (height / 2.0 + cyl_h)) < TOL, \
            f"Z max: expected {height/2.0 + cyl_h:.5f}, got {bb.zmax:.5f}"
    
        # Volume check
        prism_vol = length * width * height
        cyl_vol   = 2 * math.pi * cyl_r**2 * cyl_h
        expected_vol = prism_vol + cyl_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.5f}, got {actual_vol:.5f}"
    
        # Cylindrical faces: 2 cylinders → 2 curved lateral faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Symmetry: center of mass should be near (0, 0, small positive z)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X should be ~0, got {com.x:.5f}"
        assert abs(com.y) < TOL, f"CoM Y should be ~0, got {com.y:.5f}"
        assert com.z > 0, f"CoM Z should be slightly positive (cylinders on top), got {com.z:.5f}"
    
        # Check cylinder positions via bounding box X extents
        # The cylinders should not extend beyond the prism in X
        assert abs(bb.xmin - (-length / 2.0)) < TOL, \
            f"X min: expected {-length/2.0:.5f}, got {bb.xmin:.5f}"
        assert abs(bb.xmax - (length / 2.0)) < TOL, \
            f"X max: expected {length/2.0:.5f}, got {bb.xmax:.5f}"
    
        # Check that cylinder diameter doesn't exceed width
        assert cyl_d < width, \
            f"Cylinder diameter {cyl_d} should be less than width {width}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.5f} x {bb.ylen:.5f} x {bb.zlen:.5f}")
        print(f"  Volume: {actual_vol:.5f} (expected ~{expected_vol:.5f})")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Center of mass: ({com.x:.5f}, {com.y:.5f}, {com.z:.5f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520321/gpt_generated.stl')
