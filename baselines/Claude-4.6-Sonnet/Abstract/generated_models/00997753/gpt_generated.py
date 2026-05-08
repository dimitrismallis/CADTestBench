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
        outer_size   = 80.0      # outer square side length
        inner_size   = 74.0      # inner square side length (3mm wall each side)
        height       = 20.0      # extrusion height
        cut_depth    = 17.0      # inner cut depth (leaves 3mm bottom)
        outer_radius = 5.0       # outer corner radius
        inner_radius = 4.0       # inner corner radius
    
        # --- Step 1: Draw outer square with rounded corners and extrude ---
        outer_sketch = (
            cq.Sketch()
            .rect(outer_size, outer_size)
            .vertices()
            .fillet(outer_radius)
        )
    
        result = (
            cq.Workplane("XY")
            .placeSketch(outer_sketch)
            .extrude(height)
        )
    
        # --- Step 2: On the top face, draw inner square with rounded corners ---
        # Negatively extrude (cut) downward by cut_depth, leaving a bottom
        inner_sketch = (
            cq.Sketch()
            .rect(inner_size, inner_size)
            .vertices()
            .fillet(inner_radius)
        )
    
        result = (
            result
            .faces(">Z")
            .workplane()
            .placeSketch(inner_sketch)
            .extrude(-cut_depth, combine="cut")
        )
    
        # --- Final object verification ---
        TOL = 0.5   # slightly relaxed for rounded-corner area approximations
    
        # 1. Bounding box: should be outer_size × outer_size × height
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - outer_size) < TOL, \
            f"BBox X: expected {outer_size}, got {bb.xlen}"
        assert abs(bb.ylen - outer_size) < TOL, \
            f"BBox Y: expected {outer_size}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"BBox Z: expected {height}, got {bb.zlen}"
    
        # 2. The object should be centered at X=0, Y=0
        center = result.val().Center()
        assert abs(center.x) < TOL, \
            f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, \
            f"Center Y: expected 0, got {center.y}"
    
        # 3. Volume check:
        # Outer volume (square with rounded corners) * height
        # minus inner cutout (smaller square with rounded corners) * cut_depth
        outer_area = outer_size**2 - (4 - math.pi) * outer_radius**2
        inner_area = inner_size**2 - (4 - math.pi) * inner_radius**2
        expected_vol = outer_area * height - inner_area * cut_depth
        actual_vol = result.val().Volume()
        rel_err = abs(actual_vol - expected_vol) / expected_vol
        assert rel_err < 0.02, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}, rel_err={rel_err:.4f}"
    
        # 4. Top face should be at z = height (annular ring)
        top_faces = result.faces(">Z")
        assert top_faces.size() >= 1, \
            f"Top faces: expected at least 1, got {top_faces.size()}"
        top_bb = top_faces.val().BoundingBox()
        assert abs(top_bb.zmin - height) < TOL, \
            f"Top face Z: expected {height}, got {top_bb.zmin}"
    
        # 5. Bottom face should be at z = 0
        bottom_faces = result.faces("<Z")
        assert bottom_faces.size() >= 1, \
            f"Bottom faces: expected at least 1, got {bottom_faces.size()}"
        bot_bb = bottom_faces.val().BoundingBox()
        assert abs(bot_bb.zmax - 0.0) < TOL, \
            f"Bottom face Z: expected 0, got {bot_bb.zmax}"
    
        # 6. Check that a point inside the inner cavity is NOT inside the solid
        inner_point = (0.0, 0.0, height / 2)
        assert not result.val().isInside(inner_point), \
            f"Inner cavity point {inner_point} should be outside the solid (hollow)"
    
        # 7. Check that a point in the wall IS inside the solid
        wall_point = (outer_size / 2 - 1.5, 0.0, height / 2)
        assert result.val().isInside(wall_point), \
            f"Wall point {wall_point} should be inside the solid"
    
        # 8. Check that a point in the bottom IS inside the solid
        floor_z = height - cut_depth   # = 3.0
        bottom_point = (0.0, 0.0, floor_z / 2)
        assert result.val().isInside(bottom_point), \
            f"Bottom point {bottom_point} should be inside the solid"
    
        # 9. Check that a point just above the inner floor IS inside the cavity
        above_floor_point = (0.0, 0.0, floor_z + 1.0)
        assert not result.val().isInside(above_floor_point), \
            f"Point above inner floor {above_floor_point} should be in the cavity (outside solid)"
    
        # 10. Verify there are planar faces (top ring, bottom, inner floor, walls)
        planar_faces = result.faces("%Plane")
        assert planar_faces.size() >= 3, \
            f"Planar faces: expected at least 3, got {planar_faces.size()}"
    
        # 11. Verify cylindrical faces exist (from rounded corners)
        cyl_faces = result.faces("%Cylinder")
        assert cyl_faces.size() >= 1, \
            f"Cylindrical faces: expected at least 1 (rounded corners), got {cyl_faces.size()}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997753/gpt_generated.stl')
