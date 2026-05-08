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
        height = 0.75
        outer_diameter = 0.07812
        inner_diameter = 0.046741
        outer_radius = outer_diameter / 2.0   # 0.03906
        inner_radius = inner_diameter / 2.0   # 0.0233705
        z_translation = height / 2.0          # 0.375
    
        # --- Step 1: Create outer cylinder centered at origin (height along Z) ---
        outer = cq.Workplane("XY").cylinder(height, outer_radius)
    
        # --- Step 2: Subtract inner cylinder to create hollow cylinder ---
        hollow = outer.faces(">Z").workplane().circle(inner_radius).cutThruAll()
    
        # --- Step 3: Translate along Z by half height to center vertically ---
        # The cylinder() primitive is already centered at origin (Z from -h/2 to +h/2),
        # so translating by +h/2 moves it so Z goes from 0 to h.
        result = hollow.translate((0, 0, z_translation))
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - outer_diameter) < TOL, f"X extent: expected {outer_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - outer_diameter) < TOL, f"Y extent: expected {outer_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z extent: expected {height}, got {bb.zlen}"
    
        # Z position: should go from 0 to height after translation
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"Z max: expected {height}, got {bb.zmax}"
    
        # Volume check: pi * (R_outer^2 - R_inner^2) * height
        expected_vol = math.pi * (outer_radius**2 - inner_radius**2) * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Cylindrical faces: expect 2 (outer curved surface + inner curved surface)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Planar faces: expect 2 (top and bottom annular rings)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, f"Planar faces: expected 2, got {planar_faces}"
    
        # Center of mass should be at (0, 0, height/2) due to symmetry
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - z_translation) < TOL, f"CoM Z: expected {z_translation}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00008138/gpt_generated.stl')
