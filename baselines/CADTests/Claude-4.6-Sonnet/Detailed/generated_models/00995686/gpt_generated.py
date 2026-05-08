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
        outer_diameter = 0.702675
        outer_radius = outer_diameter / 2.0          # 0.3513375
        wall_thickness = 0.049281
        inner_radius = outer_radius - wall_thickness  # 0.3020565
        inner_diameter = inner_radius * 2.0
        cyl_width = 0.75  # length along Z axis
    
        # --- Step 1: Create hollow cylinder (tube) along Z axis ---
        # Outer cylinder
        outer_cyl = cq.Workplane("XY").cylinder(cyl_width, outer_radius)
        # Inner cylinder (to subtract)
        inner_cyl = cq.Workplane("XY").cylinder(cyl_width, inner_radius)
        # Hollow cylinder = outer minus inner
        hollow_cyl = outer_cyl.cut(inner_cyl)
    
        # --- Step 2: Create cutting box ---
        # Box dimensions: height=outer_diameter, depth=outer_diameter, width=cyl_width
        # Position the box to cut a sector from the +X side of the cylinder
        # Box centered at (outer_radius/2, 0, 0) so it covers x=[0, outer_diameter]
        # Actually: place box so it starts at x=0 and extends to x=outer_diameter
        # Box center in X = outer_diameter/2 = outer_radius
        cut_box = (
            cq.Workplane("XY")
            .box(outer_diameter, outer_diameter, cyl_width, centered=True)
            .translate((outer_radius, 0, 0))
        )
    
        # --- Step 3: Cut the box from the hollow cylinder ---
        result = hollow_cyl.cut(cut_box)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Check bounding box
        bb = result.val().BoundingBox()
    
        # Z extent should still be cyl_width = 0.75
        assert abs(bb.zlen - cyl_width) < TOL, f"Z length: expected {cyl_width}, got {bb.zlen}"
    
        # X extent: the cut removes the +X half, so xmax should be ~0 (at the cut plane)
        # The remaining part is the -X half of the hollow cylinder
        # xmin should be ~ -outer_radius, xmax should be ~ 0
        assert bb.xmin < -outer_radius + TOL, f"xmin should be near -{outer_radius:.4f}, got {bb.xmin:.4f}"
        assert bb.xmax < TOL + 0.01, f"xmax should be near 0, got {bb.xmax:.4f}"
    
        # Y extent should be ~ outer_diameter (full diameter preserved in Y)
        assert abs(bb.ylen - outer_diameter) < TOL, f"Y length: expected {outer_diameter}, got {bb.ylen}"
    
        # Volume check:
        # Full hollow cylinder volume
        full_hollow_vol = math.pi * (outer_radius**2 - inner_radius**2) * cyl_width
        # The cut removes approximately half the hollow cylinder (the +X half)
        # Approximate: ~half the tube volume
        approx_remaining = full_hollow_vol * 0.5
        actual_vol = result.val().Volume()
        # Allow generous tolerance since the cut is approximate
        assert actual_vol > 0, f"Volume should be positive, got {actual_vol}"
        assert actual_vol < full_hollow_vol, f"Volume should be less than full hollow cylinder {full_hollow_vol:.6f}, got {actual_vol:.6f}"
        assert abs(actual_vol - approx_remaining) / full_hollow_vol < 0.15, \
            f"Volume ~half of hollow cyl expected ~{approx_remaining:.6f}, got {actual_vol:.6f}"
    
        # Should have cylindrical faces (the inner and outer arc surfaces)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, f"Expected at least 2 cylindrical faces, got {cyl_faces}"
    
        # Should have planar faces (top, bottom, and cut faces)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 3, f"Expected at least 3 planar faces, got {planar_faces}"
    
        print(f"Bounding box: x=[{bb.xmin:.4f}, {bb.xmax:.4f}], y=[{bb.ymin:.4f}, {bb.ymax:.4f}], z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Volume: {actual_vol:.6f} (full hollow: {full_hollow_vol:.6f})")
        print(f"Cylindrical faces: {cyl_faces}, Planar faces: {planar_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00995686/gpt_generated.stl')
