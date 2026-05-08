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
        rect_length = 100.0   # X direction
        rect_width  = 20.0    # Y direction
        rect_height = 5.0     # Z direction (thickness of base)
    
        cyl_radius  = rect_width / 3.0   # ≈ 6.667 mm, ~1/3 of width
        cyl_height  = 15.0               # height of cylinder
    
        # Place cylinder close to the +X edge of the rectangle.
        # Rectangle spans x: -50 to +50, y: -10 to +10
        # Box is centered at z=0, so top face is at z = +rect_height/2 = +2.5
        cyl_cx = rect_length / 2.0 - cyl_radius   # = 50 - 6.667 = 43.333
        cyl_cy = 0.0
        # Cylinder starts at the top face of the centered box: z = +rect_height/2
        cyl_start_z = rect_height / 2.0   # = 2.5
    
        # --- Step 1: Create the extruded rectangle (base) ---
        base = cq.Workplane("XY").box(rect_length, rect_width, rect_height)
    
        # --- Step 2: Create the cylinder on top of the rectangle near the +X edge ---
        cylinder = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(cyl_cx, cyl_cy, cyl_start_z))
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # --- Step 3: Union the cylinder with the base ---
        result = base.union(cylinder)
    
        # --- Final object verification ---
        TOL = 0.5  # generous tolerance for bounding box checks
    
        bb = result.val().BoundingBox()
    
        # Bounding box X: rectangle dominates at 100mm
        assert abs(bb.xlen - rect_length) < TOL, \
            f"X length: expected {rect_length}, got {bb.xlen}"
    
        # Bounding box Y: rectangle dominates at 20mm
        assert abs(bb.ylen - rect_width) < TOL, \
            f"Y length: expected {rect_width}, got {bb.ylen}"
    
        # Bounding box Z:
        # Box centered at z=0 → spans z=-2.5 to z=+2.5
        # Cylinder starts at z=+2.5, ends at z=+2.5+15=+17.5
        # Total zlen = 17.5 - (-2.5) = 20.0
        expected_zlen = rect_height / 2.0 + cyl_height  # 2.5 + 15 = 17.5, plus 2.5 below = 20.0
        expected_zlen_total = rect_height / 2.0 + cyl_height + rect_height / 2.0
        assert abs(bb.zlen - expected_zlen_total) < TOL, \
            f"Z length: expected {expected_zlen_total}, got {bb.zlen}"
    
        # Volume check: base box + cylinder (no overlap since cylinder is on top)
        base_vol = rect_length * rect_width * rect_height
        cyl_vol  = math.pi * cyl_radius**2 * cyl_height
        expected_vol = base_vol + cyl_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Length-to-width ratio check: 5:1
        ratio = rect_length / rect_width
        assert abs(ratio - 5.0) < 0.01, \
            f"Length/width ratio: expected 5.0, got {ratio}"
    
        # Cylinder radius ≈ 1/3 of width
        radius_ratio = cyl_radius / rect_width
        assert abs(radius_ratio - 1.0/3.0) < 0.01, \
            f"Cylinder radius / width: expected ~0.333, got {radius_ratio:.4f}"
    
        # Cylinder is close to the +X edge: center at x=43.333, edge at x=50
        # The cylinder's +X extent should be very close to the rectangle's +X edge
        assert abs(bb.xmax - rect_length / 2.0) < TOL, \
            f"Max X: expected ~{rect_length/2.0}, got {bb.xmax}"
    
        # Check that the cylinder face exists (cylindrical face)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check the solid is a single compound/solid
        solids = result.solids().size()
        assert solids >= 1, \
            f"Expected at least 1 solid, got {solids}"
    
        # Verify the cylinder top is at z = rect_height/2 + cyl_height = 2.5 + 15 = 17.5
        expected_zmax = rect_height / 2.0 + cyl_height
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"Z max: expected {expected_zmax}, got {bb.zmax}"
    
        # Verify the base bottom is at z = -rect_height/2 = -2.5 (box is centered)
        expected_zmin = -rect_height / 2.0
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"Z min: expected {expected_zmin}, got {bb.zmin}"
    
        print("All assertions passed!")
        print(f"  Base: {rect_length} x {rect_width} x {rect_height} mm")
        print(f"  Cylinder radius: {cyl_radius:.3f} mm (= width/3)")
        print(f"  Cylinder center X: {cyl_cx:.3f} mm (close to +X edge at {rect_length/2:.1f})")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f})")
        print(f"  Bounding box Z: {bb.zmin:.2f} to {bb.zmax:.2f}, zlen={bb.zlen:.2f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00009998/gpt_generated.stl')
