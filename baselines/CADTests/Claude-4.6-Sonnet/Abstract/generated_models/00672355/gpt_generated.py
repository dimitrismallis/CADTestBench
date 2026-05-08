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
        cyl_radius   = 20.0          # cylinder radius
        cyl_diameter = 2 * cyl_radius  # 40
        cyl_height   = 30.0          # cylinder height
    
        rect_width   = (4/5) * cyl_diameter   # 32.0  (along X)
        rect_thick   = (1/10) * rect_width    # 3.2   (along Y, the "small" dimension)
        fin_height   = cyl_height / 2         # 15.0  (extrusion of the rectangle)
    
        # --- Step 1: Base cylinder ---
        result = (
            cq.Workplane("XY")
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # --- Step 2 & 3: Draw centered rectangle on top face and extrude it ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .rect(rect_width, rect_thick)
            .extrude(fin_height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box checks
        # X extent: cylinder diameter = 40
        assert abs(bb.xlen - cyl_diameter) < TOL, \
            f"X extent: expected {cyl_diameter}, got {bb.xlen}"
    
        # Y extent: cylinder diameter = 40 (rectangle is narrower than cylinder)
        assert abs(bb.ylen - cyl_diameter) < TOL, \
            f"Y extent: expected {cyl_diameter}, got {bb.ylen}"
    
        # Z extent: cylinder height + fin height = 30 + 15 = 45
        expected_zlen = cyl_height + fin_height
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z extent: expected {expected_zlen}, got {bb.zlen}"
    
        # Z min should be 0 (base of cylinder on XY plane)
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
    
        # Z max should be cyl_height + fin_height = 45
        assert abs(bb.zmax - (cyl_height + fin_height)) < TOL, \
            f"Z max: expected {cyl_height + fin_height}, got {bb.zmax}"
    
        # Volume check:
        # Cylinder volume = pi * r^2 * h
        cyl_vol = math.pi * cyl_radius**2 * cyl_height
        # Fin (rectangular box) volume = width * thick * fin_height
        fin_vol = rect_width * rect_thick * fin_height
        expected_vol = cyl_vol + fin_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check there is exactly 1 solid
        assert result.solids().size() == 1, \
            f"Solid count: expected 1, got {result.solids().size()}"
    
        # Check cylindrical face exists (the curved side of the cylinder)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Cylindrical faces: expected at least 1, got {cyl_faces}"
    
        # Check the bottom face is at z=0
        bot_bb = result.faces("<Z").val().BoundingBox()
        assert abs(bot_bb.zmin - 0.0) < TOL, \
            f"Bottom face Z: expected 0.0, got {bot_bb.zmin}"
    
        # Check the top face of the fin is at z = cyl_height + fin_height = 45
        top_bb = result.faces(">Z").val().BoundingBox()
        assert abs(top_bb.zmax - (cyl_height + fin_height)) < TOL, \
            f"Top face Z: expected {cyl_height + fin_height}, got {top_bb.zmax}"
    
        # Check the fin top face dimensions match rect_width x rect_thick
        assert abs(top_bb.xlen - rect_width) < TOL, \
            f"Fin top face X: expected {rect_width}, got {top_bb.xlen}"
        assert abs(top_bb.ylen - rect_thick) < TOL, \
            f"Fin top face Y: expected {rect_thick}, got {top_bb.ylen}"
    
        # Check the fin is centered (center of fin top face should be at x=0, y=0)
        top_center = result.faces(">Z").val().Center()
        assert abs(top_center.x) < TOL, \
            f"Fin top center X: expected 0.0, got {top_center.x}"
        assert abs(top_center.y) < TOL, \
            f"Fin top center Y: expected 0.0, got {top_center.y}"
    
        print("All assertions passed!")
        print(f"  Cylinder: radius={cyl_radius}, height={cyl_height}")
        print(f"  Rectangle: width={rect_width}, thick={rect_thick}")
        print(f"  Fin height: {fin_height}")
        print(f"  Total height: {cyl_height + fin_height}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00672355/gpt_generated.stl')
