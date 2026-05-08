import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        plate_length = 80.0
        plate_width  = 30.0
        plate_height = 5.0
        sq_size      = 12.0
        sq_fillet    = 2.0
        cut_depth    = plate_height
    
        half_sq = sq_size / 2.0
    
        # Cutout centers (inset from two corners on the +Y long edge)
        cx1 =  plate_length / 2.0 - half_sq   # = 34
        cy1 =  plate_width  / 2.0 - half_sq   # = 9
        cx2 = -(plate_length / 2.0 - half_sq) # = -34
        cy2 =  plate_width  / 2.0 - half_sq   # = 9
    
        # --- Step 1: Base plate ---
        result = (
            cq.Workplane("XY")
            .rect(plate_length, plate_width)
            .extrude(plate_height)
        )
    
        # --- Step 2: Build rounded-square cutting tools and subtract ---
        # Create each cutter as a separate solid, then use .cut()
        def make_rounded_square_cutter(cx, cy, size, fillet_r, height):
            """Create a rounded-square prism centered at (cx, cy, height/2)."""
            cutter = (
                cq.Workplane(cq.Plane(origin=(cx, cy, 0), normal=(0, 0, 1)))
                .rect(size, size)
                .extrude(height)
                .edges("|Z")
                .fillet(fillet_r)
            )
            return cutter
    
        cutter1 = make_rounded_square_cutter(cx1, cy1, sq_size, sq_fillet, cut_depth)
        cutter2 = make_rounded_square_cutter(cx2, cy2, sq_size, sq_fillet, cut_depth)
    
        # Subtract the cutters from the plate
        result = result.cut(cutter1)
        result = result.cut(cutter2)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 1. Bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - plate_length) < TOL, \
            f"X length: expected {plate_length}, got {bb.xlen}"
        assert abs(bb.ylen - plate_width) < TOL, \
            f"Y length: expected {plate_width}, got {bb.ylen}"
        assert abs(bb.zlen - plate_height) < TOL, \
            f"Z height: expected {plate_height}, got {bb.zlen}"
    
        # 2. Volume: base plate minus two rounded-square cutouts
        # Rounded square area = sq_size^2 - (4 - pi) * sq_fillet^2
        rounded_sq_area = sq_size**2 - (4.0 - math.pi) * sq_fillet**2
        base_vol = plate_length * plate_width * plate_height
        cutout_vol = 2.0 * rounded_sq_area * cut_depth
        expected_vol = base_vol - cutout_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Exactly 1 solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # 4. Top face at z = plate_height
        top_bb = result.faces(">Z").val().BoundingBox()
        assert abs(top_bb.zmax - plate_height) < TOL, \
            f"Top face Z: expected {plate_height}, got {top_bb.zmax}"
    
        # 5. Cylindrical faces from rounded cutout edges (at least 4, one per rounded corner per cutout)
        cyl_faces = result.faces("%Cylinder")
        assert cyl_faces.size() >= 4, \
            f"Expected >= 4 cylindrical faces, got {cyl_faces.size()}"
    
        # 6. Points inside cutouts should NOT be inside solid
        solid = result.val()
    
        p1 = (cx1, cy1, plate_height / 2.0)
        assert not solid.isInside(p1), \
            f"Point {p1} should be in cutout (not solid)"
    
        p2 = (cx2, cy2, plate_height / 2.0)
        assert not solid.isInside(p2), \
            f"Point {p2} should be in cutout (not solid)"
    
        # Center of plate should be solid
        p3 = (0.0, 0.0, plate_height / 2.0)
        assert solid.isInside(p3), \
            f"Point {p3} should be inside solid"
    
        # 7. Bottom face at z = 0
        bot_bb = result.faces("<Z").val().BoundingBox()
        assert abs(bot_bb.zmin - 0.0) < TOL, \
            f"Bottom face Z: expected 0.0, got {bot_bb.zmin}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00998088/gpt_generated.stl')
