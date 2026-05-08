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
        square_size = 100.0      # 100x100 square
        extrude_h   = 5.0        # slight extrusion
        tri_leg     = 60.0       # legs of the right triangle
    
        # --- Step 1: Create the large square extruded slightly ---
        # Box centered at origin: x in [-50,50], y in [-50,50], z in [0,5]
        result = cq.Workplane("XY").box(square_size, square_size, extrude_h,
                                        centered=(True, True, False))
    
        # --- Step 2: Define the right triangle cutout at the bottom-right corner ---
        # Square corners (centered=True in X,Y):
        #   bottom-right = (50, -50)
        #   The right angle of the triangle sits at (50, -50)
        #   One leg goes LEFT along the bottom edge: from (50,-50) to (50-tri_leg, -50) = (-10, -50)
        #   Other leg goes UP along the right edge:  from (50,-50) to (50, -50+tri_leg) = (50, 10)
        # Triangle vertices (in XY plane):
        half = square_size / 2.0
        p1 = (half,        -half)           # right angle corner (bottom-right)
        p2 = (half - tri_leg, -half)        # along bottom edge
        p3 = (half,        -half + tri_leg) # along right edge
    
        # Build the triangle as a wire and cut through all
        triangle_cut = (
            cq.Workplane("XY")
            .moveTo(p1[0], p1[1])
            .lineTo(p2[0], p2[1])
            .lineTo(p3[0], p3[1])
            .close()
            .extrude(extrude_h)
        )
    
        result = result.cut(triangle_cut)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box: x from -50 to 50, y from -50 to 50, z from 0 to 5
        assert abs(bb.xmin - (-half)) < TOL, f"xmin expected {-half}, got {bb.xmin}"
        assert abs(bb.xmax - half)    < TOL, f"xmax expected {half}, got {bb.xmax}"
        assert abs(bb.ymin - (-half)) < TOL, f"ymin expected {-half}, got {bb.ymin}"
        assert abs(bb.ymax - half)    < TOL, f"ymax expected {half}, got {bb.ymax}"
        assert abs(bb.zmin - 0.0)     < TOL, f"zmin expected 0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_h) < TOL, f"zmax expected {extrude_h}, got {bb.zmax}"
    
        # Volume check:
        # Square area = 100*100 = 10000
        # Triangle area = 0.5 * 60 * 60 = 1800
        # Remaining area = 10000 - 1800 = 8200
        # Volume = 8200 * 5 = 41000
        square_area   = square_size * square_size
        triangle_area = 0.5 * tri_leg * tri_leg
        expected_vol  = (square_area - triangle_area) * extrude_h
        actual_vol    = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # The bottom-right corner (50, -50) should NOT be inside the solid (it was cut away)
        assert not result.val().isInside((half - 1, -half + 1, extrude_h / 2)), \
            "Point near bottom-right corner should be outside (cut away)"
    
        # A point in the top-left area should be inside the solid
        assert result.val().isInside((-half + 5, half - 5, extrude_h / 2)), \
            "Point in top-left area should be inside the solid"
    
        # A point in the middle should be inside
        assert result.val().isInside((0, 0, extrude_h / 2)), \
            "Center point should be inside the solid"
    
        # The right-angle corner of the triangle (50, -50) should be on the boundary (not inside)
        assert not result.val().isInside((half, -half, extrude_h / 2)), \
            "Exact corner (50,-50) should not be inside the solid"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
        print(f"Volume: {actual_vol:.1f} (expected {expected_vol:.1f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00673788/gpt_generated.stl')
