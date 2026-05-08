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
        base_diameter = 1.5
        base_radius   = base_diameter / 2.0       # 0.75
        base_height   = 0.114796
    
        top_diameter  = 1.17857
        top_radius    = top_diameter / 2.0        # 0.589285
        top_height    = 0.306123
    
        # --- Step 1: Create the base (larger) cylinder ---
        # Centered at origin: spans Z from -base_height/2 to +base_height/2
        base_cyl = (
            cq.Workplane("XY")
            .circle(base_radius)
            .extrude(base_height)
        )
    
        # --- Step 2: Create the smaller top cylinder ---
        # It sits on top of the base, so its bottom face is at Z = base_height
        # We build it starting at Z=0 then translate up by base_height
        top_cyl = (
            cq.Workplane("XY")
            .circle(top_radius)
            .extrude(top_height)
            .translate((0, 0, base_height))
        )
    
        # --- Step 3: Union the two cylinders ---
        result = base_cyl.union(top_cyl)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Overall bounding box checks
        total_height = base_height + top_height   # 0.114796 + 0.306123 = 0.420919
        assert abs(bb.xlen - base_diameter) < TOL, \
            f"X extent: expected {base_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - base_diameter) < TOL, \
            f"Y extent: expected {base_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - total_height) < TOL, \
            f"Z extent (total height): expected {total_height}, got {bb.zlen}"
    
        # Z extents: base starts at 0, top ends at total_height
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - total_height) < TOL, \
            f"Z max: expected {total_height}, got {bb.zmax}"
    
        # Volume check: sum of two cylinders (no overlap since top is smaller and sits on top)
        vol_base = math.pi * base_radius**2 * base_height
        vol_top  = math.pi * top_radius**2  * top_height
        expected_vol = vol_base + vol_top
        actual_vol   = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 2 flat ends (bottom of base, top of top) + 2 cylindrical side faces
        # + 1 annular ring face at the step (where top sits on base) = 5 faces total
        face_count = result.faces().size()
        assert face_count == 5, \
            f"Face count: expected 5, got {face_count}"
    
        # Cylindrical faces: 2 (one for base side, one for top side)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Planar faces: 3 (bottom of base, annular ring at step, top of top cylinder)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 3, \
            f"Planar face count: expected 3, got {planar_face_count}"
    
        # Center of mass should be on the Z axis (x=0, y=0)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
    
        # The center of mass Z should be between 0 and total_height
        assert 0 < com.z < total_height, \
            f"Center of mass Z: expected between 0 and {total_height}, got {com.z}"
    
        # Point inside base cylinder should be inside the solid
        assert solid.isInside((0, 0, base_height / 2)), \
            "Point inside base cylinder should be inside solid"
    
        # Point inside top cylinder should be inside the solid
        assert solid.isInside((0, 0, base_height + top_height / 2)), \
            "Point inside top cylinder should be inside solid"
    
        # Point outside (beyond base radius) should NOT be inside the solid
        assert not solid.isInside((base_radius + 0.1, 0, base_height / 2)), \
            "Point outside base cylinder should not be inside solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00004935/gpt_generated.stl')
