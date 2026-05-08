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
        height = 0.75
        outer_radius = 0.078575 / 2   # 0.0392875
        inner_radius = 0.058318 / 2   # 0.029159
        cut_diameter = 0.078654
        cut_radius = cut_diameter / 2  # 0.039327
    
        # --- Step 1: Create hollow cylinder (tube) ---
        # Outer cylinder minus inner cylinder bore
        outer = cq.Workplane("XY").cylinder(height, outer_radius)
        inner_bore = cq.Workplane("XY").cylinder(height, inner_radius)
        hollow_cyl = outer.cut(inner_bore)
    
        # --- Step 2: Create semi-circular cutting tool ---
        # A half-cylinder of radius cut_radius oriented along Z axis
        # The flat face is at y=0, the curved part extends in +Y direction
        # This removes the +Y half of the hollow cylinder
    
        # Full cylinder for cutting (oriented along Z)
        full_cut_cyl = cq.Workplane("XY").cylinder(height * 3, cut_radius)
    
        # Box covering the +Y half to intersect with the cylinder
        half_box = (
            cq.Workplane("XY")
            .box(cut_radius * 3, cut_radius * 3, height * 4, centered=True)
            .translate((0, cut_radius * 1.5, 0))
        )
    
        # The cutting tool is the +Y half-cylinder
        cut_tool = full_cut_cyl.intersect(half_box)
    
        # --- Step 3: Apply the semi-circular cut to the hollow cylinder ---
        # This removes the +Y half of the hollow cylinder
        result = hollow_cyl.cut(cut_tool)
    
        # --- Final object verification ---
        TOL = 1e-5
        bb = result.val().BoundingBox()
        actual_vol = result.val().Volume()
        hollow_vol = math.pi * (outer_radius**2 - inner_radius**2) * height
    
        print(f"Bounding box: x={bb.xlen:.8f}, y={bb.ylen:.8f}, z={bb.zlen:.8f}")
        print(f"xmin={bb.xmin:.8f}, xmax={bb.xmax:.8f}")
        print(f"ymin={bb.ymin:.8f}, ymax={bb.ymax:.8f}")
        print(f"zmin={bb.zmin:.8f}, zmax={bb.zmax:.8f}")
        print(f"Actual volume: {actual_vol:.8e}")
        print(f"Hollow cylinder volume: {hollow_vol:.8e}")
        print(f"Cylindrical faces: {result.faces('%Cylinder').size()}")
    
        # Check overall height (Z extent) - should still be 0.75
        assert abs(bb.zlen - height) < TOL, \
            f"Height: expected {height}, got {bb.zlen}"
    
        # Check X extent - should be approximately outer diameter (0.078575)
        assert abs(bb.xlen - 2 * outer_radius) < TOL, \
            f"X extent: expected {2*outer_radius:.8f}, got {bb.xlen:.8f}"
    
        # Y extent: the semi-circle cut removed the +Y half
        # ymin should be near -outer_radius, ymax should be near 0
        assert bb.ymin < -outer_radius * 0.9, \
            f"Y min should be near -{outer_radius:.6f}, got {bb.ymin:.8f}"
        assert bb.ymax < TOL, \
            f"Y max should be near 0 (cut removed +Y half), got {bb.ymax:.8f}"
    
        # Check that the object has cylindrical faces (outer and inner surfaces)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces (outer + inner), got {cyl_faces}"
    
        # Volume checks
        assert actual_vol > 0, \
            f"Volume should be positive, got {actual_vol}"
        assert actual_vol < hollow_vol, \
            f"Volume should be less than hollow cylinder: {actual_vol:.4e} < {hollow_vol:.4e}"
    
        # The cut removes roughly half the hollow cylinder
        # (cut_radius ≈ outer_radius, so roughly half the annular cross-section is removed)
        assert actual_vol > hollow_vol * 0.3, \
            f"Volume too small: {actual_vol:.4e} vs hollow {hollow_vol:.4e}"
        assert actual_vol < hollow_vol * 0.75, \
            f"Volume too large: {actual_vol:.4e} vs hollow {hollow_vol:.4e}"
    
        # Check that the center bore is hollow (point at center should be outside solid)
        center_point = (0, 0, 0)
        is_inside = result.val().isInside(center_point)
        assert not is_inside, \
            f"Center point should be outside (in the bore), but isInside={is_inside}"
    
        # A point in the wall on the -Y side (not cut) should be inside the solid
        wall_y = -(inner_radius + outer_radius) / 2
        wall_point = (0, wall_y, 0)
        is_wall_inside = result.val().isInside(wall_point)
        assert is_wall_inside, \
            f"Wall point {wall_point} should be inside solid, but isInside={is_wall_inside}"
    
        # A point in the +Y half (where the cut was made) should be outside the solid
        cut_point = (0, (inner_radius + outer_radius) / 2, 0)
        is_cut_inside = result.val().isInside(cut_point)
        assert not is_cut_inside, \
            f"Cut region point {cut_point} should be outside solid, but isInside={is_cut_inside}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520402/gpt_generated.stl')
