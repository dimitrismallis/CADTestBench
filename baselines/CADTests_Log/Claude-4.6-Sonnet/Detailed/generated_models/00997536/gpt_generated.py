import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        cyl_diameter = 0.988192
        cyl_radius   = cyl_diameter / 2.0   # 0.494096
        height       = 0.75
        oct_diameter = 0.79436              # circumscribed circle diameter
        n_sides      = 8
    
        # --- Step 1: Create the cylinder ---
        result = cq.Workplane("XY").circle(cyl_radius).extrude(height)
    
        # --- Step 2: Create the octagonal hole ---
        result = (
            result
            .faces(">Z").workplane()
            .polygon(n_sides, oct_diameter)
            .cutThruAll()
        )
    
        # --- Debug face breakdown ---
        total = result.faces().size()
        cyl_f = result.faces("%Cylinder").size()
        pln_f = result.faces("%Plane").size()
        print(f"Total faces: {total}, Cylinder: {cyl_f}, Plane: {pln_f}")
        for i, f in enumerate(result.faces().vals()):
            print(f"  Face {i}: type={f.geomType()}, area={f.Area():.6f}")
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - cyl_diameter) < TOL, \
            f"X bbox: expected {cyl_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - cyl_diameter) < TOL, \
            f"Y bbox: expected {cyl_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z bbox: expected {height}, got {bb.zlen}"
    
        # Volume: cylinder vol minus octagon prism vol
        # polygon(8, diameter) uses circumscribed circle diameter
        # circumradius R = oct_diameter/2
        R_oct = oct_diameter / 2.0   # 0.39718
        oct_area = 2.0 * math.sqrt(2.0) * R_oct ** 2
        cyl_area = math.pi * cyl_radius ** 2
        expected_vol = (cyl_area - oct_area) * height
        actual_vol = result.val().Volume()
        print(f"R_oct={R_oct:.6f}, oct_area={oct_area:.6f}, cyl_area={cyl_area:.6f}")
        print(f"expected_vol={expected_vol:.6f}, actual_vol={actual_vol:.6f}")
    
        vol_rel_err = abs(actual_vol - expected_vol) / expected_vol
        assert vol_rel_err < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}, rel_err={vol_rel_err:.4f}"
    
        # Symmetry
        center = result.val().Center()
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z - height / 2.0) < TOL, \
            f"Center Z: expected {height/2.0}, got {center.z}"
    
        # Point containment: center should be in hole
        assert not result.val().isInside((0.0, 0.0, height / 2.0)), \
            "Center should be inside hole, not solid"
    
        # Point containment: point in annular ring should be inside solid
        mid_radius = (cyl_radius + R_oct) / 2.0
        assert result.val().isInside((mid_radius, 0.0, height / 2.0)), \
            f"Point at mid_radius={mid_radius:.4f} should be inside solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997536/gpt_generated.stl')
