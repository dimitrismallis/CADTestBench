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
        large_diameter = 40.0
        large_radius   = large_diameter / 2      # 20 mm
        large_height   = 20.0
    
        small_diameter = large_diameter / 2      # 20 mm (half diameter)
        small_radius   = small_diameter / 2      # 10 mm
        small_height   = large_height * 5        # 100 mm (five times length)
    
        # --- Step 1 & 2: Create and extrude the large cylinder ---
        # Centered at origin in XY, extending from z=0 to z=large_height
        large_cyl = (
            cq.Workplane("XY")
            .circle(large_radius)
            .extrude(large_height)
        )
    
        # --- Step 3: Create the smaller, longer cylinder on the bottom ---
        # It sits below the large cylinder: from z=0 downward to z=-small_height
        # We build it going downward from z=0
        small_cyl = (
            cq.Workplane("XY")
            .circle(small_radius)
            .extrude(small_height, combine=False)
            # extrude goes upward by default; we need it going downward
            # So we mirror it about XY plane (z=0)
        )
        # Mirror the small cylinder about XY so it goes from z=0 to z=-small_height
        small_cyl = small_cyl.mirror("XY", basePointVector=(0, 0, 0))
    
        # --- Step 4: Union the two cylinders ---
        result = large_cyl.union(small_cyl)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X and Y extents should be the large cylinder diameter (40 mm)
        assert abs(bb.xlen - large_diameter) < TOL, \
            f"X extent: expected {large_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - large_diameter) < TOL, \
            f"Y extent: expected {large_diameter}, got {bb.ylen}"
    
        # Z extent: large_height (20) + small_height (100) = 120 mm
        total_height = large_height + small_height
        assert abs(bb.zlen - total_height) < TOL, \
            f"Z extent: expected {total_height}, got {bb.zlen}"
    
        # Z min should be -small_height = -100
        assert abs(bb.zmin - (-small_height)) < TOL, \
            f"Z min: expected {-small_height}, got {bb.zmin}"
    
        # Z max should be large_height = 20
        assert abs(bb.zmax - large_height) < TOL, \
            f"Z max: expected {large_height}, got {bb.zmax}"
    
        # Volume check
        vol_large = math.pi * large_radius**2 * large_height
        vol_small = math.pi * small_radius**2 * small_height
        expected_vol = vol_large + vol_small  # no overlap since they share only a face
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Cylindrical faces: 2 cylinders → 2 curved faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Planar faces: top of large cyl (1) + bottom of small cyl (1) + annular ring at junction (1) = 3
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 3, \
            f"Planar faces: expected 3, got {planar_faces}"
    
        # Total faces: 2 cylindrical + 3 planar = 5
        total_faces = result.faces().size()
        assert total_faces == 5, \
            f"Total faces: expected 5, got {total_faces}"
    
        # Center of mass check: should be on Z axis (x=0, y=0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
    
        # The small cylinder is half the diameter of the large one
        assert abs(small_diameter - large_diameter / 2) < TOL, \
            f"Small diameter should be half of large: {small_diameter} vs {large_diameter/2}"
    
        # The small cylinder is five times the length of the large one
        assert abs(small_height - large_height * 5) < TOL, \
            f"Small height should be 5x large: {small_height} vs {large_height*5}"
    
        # Point inside large cylinder (top region)
        assert result.val().isInside((0, 0, 10)), \
            "Point (0,0,10) should be inside the large cylinder"
    
        # Point inside small cylinder (bottom region)
        assert result.val().isInside((0, 0, -50)), \
            "Point (0,0,-50) should be inside the small cylinder"
    
        # Point outside (beyond large cylinder radius at mid-height of large cyl)
        assert not result.val().isInside((25, 0, 10)), \
            "Point (25,0,10) should be outside the model"
    
        # Point outside (beyond small cylinder radius at mid-height of small cyl)
        assert not result.val().isInside((15, 0, -50)), \
            "Point (15,0,-50) should be outside the small cylinder region"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00521217/gpt_generated.stl')
