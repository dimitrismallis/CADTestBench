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
        length = 40.0    # prism length
        width  = 20.0    # prism width (length = 2 * width)
        height = 10.0    # prism height
    
        # Cylinders: 1/4th the size of the rectangular prism
        # Diameter = 1/4 of length = 10mm, radius = 5mm
        # Height = 1/4 of prism height = 2.5mm
        cyl_radius = (length / 4) / 2   # diameter = 10, radius = 5
        cyl_height = height / 4          # 2.5mm
    
        # Symmetric offset along length axis: place cylinders at ±(length/4) from center
        cyl_offset = length / 4          # 10mm from center along X
    
        # --- Step 1: Create the rectangular prism (centered at origin) ---
        # Prism spans Z from -height/2 to +height/2, i.e., -5 to +5
        prism = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Create two cylinders hanging below the prism bottom ---
        # Prism bottom face is at Z = -height/2 = -5
        # Place workplane at Z = -height/2, extrude downward (negative Z)
        # Cylinder spans from Z = -height/2 down to Z = -height/2 - cyl_height
        # i.e., from -5 to -7.5
    
        # Left cylinder (at -cyl_offset along X, centered in Y)
        cyl_left = (
            cq.Workplane(cq.Plane(origin=(-cyl_offset, 0, -height / 2),
                                   xDir=(1, 0, 0),
                                   normal=(0, 0, -1)))  # normal pointing down
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # Right cylinder (at +cyl_offset along X, centered in Y)
        cyl_right = (
            cq.Workplane(cq.Plane(origin=(cyl_offset, 0, -height / 2),
                                   xDir=(1, 0, 0),
                                   normal=(0, 0, -1)))  # normal pointing down
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # --- Step 3: Union all parts ---
        result = prism.union(cyl_left).union(cyl_right)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        # X: prism spans -20 to +20 = 40mm (cylinders at ±10 with radius 5 stay within ±15)
        assert abs(bb.xlen - length) < TOL, \
            f"X length: expected {length}, got {bb.xlen}"
    
        # Y: prism spans -10 to +10 = 20mm (cylinders radius 5 stay within ±5)
        assert abs(bb.ylen - width) < TOL, \
            f"Y width: expected {width}, got {bb.ylen}"
    
        # Z: prism top at +5, cylinders bottom at -5 - 2.5 = -7.5
        # Total Z span = 5 - (-7.5) = 12.5
        expected_zlen = height + cyl_height
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z height: expected {expected_zlen}, got {bb.zlen}"
    
        # Z extents
        assert abs(bb.zmax - height / 2) < TOL, \
            f"Z max: expected {height/2}, got {bb.zmax}"
        assert abs(bb.zmin - (-(height / 2 + cyl_height))) < TOL, \
            f"Z min: expected {-(height/2 + cyl_height)}, got {bb.zmin}"
    
        # Volume check: prism + 2 cylinders (no overlap since cylinders are below prism)
        prism_vol = length * width * height
        cyl_vol = 2 * math.pi * (cyl_radius ** 2) * cyl_height
        expected_vol = prism_vol + cyl_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Cylindrical faces: 2 cylinders → 2 curved side faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Symmetry: center of mass should be at X=0, Y=0 (symmetric design)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, \
            f"Center of mass Y: expected 0, got {com.y}"
    
        # The prism length is twice its width
        assert abs(length - 2 * width) < TOL, \
            f"Length should be 2x width: {length} != 2*{width}"
    
        # Cylinder diameter is 1/4 of prism length
        assert abs(2 * cyl_radius - length / 4) < TOL, \
            f"Cylinder diameter should be 1/4 of length: {2*cyl_radius} != {length/4}"
    
        # Cylinder height is 1/4 of prism height
        assert abs(cyl_height - height / 4) < TOL, \
            f"Cylinder height should be 1/4 of prism height: {cyl_height} != {height/4}"
    
        print("All assertions passed!")
        print(f"Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520321/gpt_generated.stl')
