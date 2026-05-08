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
        base_diameter = 0.567213
        base_radius   = base_diameter / 2.0   # 0.2836065
        base_height   = 0.5625
    
        top_diameter  = 0.266022
        top_radius    = top_diameter / 2.0    # 0.133011
        top_height    = 0.1875
    
        # --- Step 1: Create base cylinder ---
        result = cq.Workplane("XY").circle(base_radius).extrude(base_height)
    
        # --- Step 2: On top face, create smaller cylinder ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(top_radius)
            .extrude(top_height)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X and Y extents should equal the base diameter (widest part)
        assert abs(bb.xlen - base_diameter) < TOL, \
            f"BBox X: expected {base_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - base_diameter) < TOL, \
            f"BBox Y: expected {base_diameter}, got {bb.ylen}"
    
        # Total height = base_height + top_height
        total_height = base_height + top_height
        assert abs(bb.zlen - total_height) < TOL, \
            f"BBox Z: expected {total_height}, got {bb.zlen}"
    
        # Z extents: bottom at 0, top at total_height
        assert abs(bb.zmin - 0.0) < TOL, \
            f"BBox zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - total_height) < TOL, \
            f"BBox zmax: expected {total_height}, got {bb.zmax}"
    
        # Volume check: sum of two cylinders
        vol_base = math.pi * base_radius**2 * base_height
        vol_top  = math.pi * top_radius**2  * top_height
        expected_vol = vol_base + vol_top
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: base cylinder has 3 faces (bottom disk, curved side, top annulus/ring)
        # top cylinder adds 2 more faces (curved side, top disk)
        # Total = 5 faces (bottom flat, base curved, annular top of base, top curved, top flat)
        face_count = result.faces().size()
        assert face_count == 5, \
            f"Face count: expected 5, got {face_count}"
    
        # Cylindrical faces: 2 (one for each cylinder's lateral surface)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Planar faces: 3 (bottom, annular ring on top of base, top of small cylinder)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 3, \
            f"Planar face count: expected 3, got {planar_face_count}"
    
        # Center of mass should be on the Z axis (x=0, y=0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
    
        # CoM Z should be between 0 and total_height
        assert 0 < com.z < total_height, \
            f"CoM Z: expected between 0 and {total_height}, got {com.z}"
    
        # Check that a point at the center of the base cylinder is inside the solid
        assert result.val().isInside((0, 0, base_height / 2)), \
            "Center of base cylinder should be inside the solid"
    
        # Check that a point at the center of the top cylinder is inside the solid
        assert result.val().isInside((0, 0, base_height + top_height / 2)), \
            "Center of top cylinder should be inside the solid"
    
        # Check that a point outside the top cylinder radius but within base height is outside top
        # (at z = base_height + top_height/2, x = top_radius*1.5 should be outside)
        outside_top = result.val().isInside((top_radius * 1.5, 0, base_height + top_height / 2))
        assert not outside_top, \
            "Point outside top cylinder radius should not be inside the solid at top height"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00995843/gpt_generated.stl')
