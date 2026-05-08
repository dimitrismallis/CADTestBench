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
        bulb_radius = 5.0       # radius of the circular bulb
        bulb_height = 3.0       # extrusion height of the bulb
        stem_width  = 4.0       # width of the rectangular stem
        stem_length = 80.0      # length of the very long stem
        stem_height = 2.0       # extrusion height of the stem (less than bulb)
        overlap     = 1.0       # overlap between stem and bulb to ensure solid union
    
        # --- Step 1: Create the bulb (small circle extruded) ---
        # Circle centered at origin on XY plane, extruded in +Z
        bulb = cq.Workplane("XY").circle(bulb_radius).extrude(bulb_height)
    
        # --- Step 2: Create the stem (long rectangle extruded slightly less) ---
        # The stem overlaps the bulb by `overlap` mm so the union merges into one solid.
        # Stem spans y = [bulb_radius - overlap, bulb_radius - overlap + stem_length]
        # Center of stem: y = (bulb_radius - overlap) + stem_length/2
        stem_start_y  = bulb_radius - overlap
        stem_center_y = stem_start_y + stem_length / 2.0
    
        stem = (
            cq.Workplane("XY")
            .center(0, stem_center_y)
            .rect(stem_width, stem_length)
            .extrude(stem_height)
        )
    
        # --- Step 3: Union bulb and stem into one solid ---
        result = bulb.union(stem)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Check bounding box
        bb = result.val().BoundingBox()
    
        # X extent: dominated by bulb diameter = 2 * bulb_radius = 10
        assert abs(bb.xlen - 2 * bulb_radius) < TOL, \
            f"X extent: expected {2*bulb_radius}, got {bb.xlen}"
    
        # Y extent: from -bulb_radius to stem top = bulb_radius - overlap + stem_length
        expected_ymax = stem_start_y + stem_length   # = bulb_radius - overlap + stem_length
        expected_ymin = -bulb_radius
        expected_ylen = expected_ymax - expected_ymin
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y extent: expected {expected_ylen}, got {bb.ylen}"
    
        # Z extent: max of bulb_height and stem_height = bulb_height = 3
        assert abs(bb.zlen - bulb_height) < TOL, \
            f"Z extent: expected {bulb_height}, got {bb.zlen}"
    
        # Z min should be 0 (base on XY plane)
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
    
        # Z max should be bulb_height = 3
        assert abs(bb.zmax - bulb_height) < TOL, \
            f"Z max: expected {bulb_height}, got {bb.zmax}"
    
        # Y min should be -bulb_radius (bottom of bulb circle)
        assert abs(bb.ymin - expected_ymin) < TOL, \
            f"Y min: expected {expected_ymin}, got {bb.ymin}"
    
        # Y max should be stem top
        assert abs(bb.ymax - expected_ymax) < TOL, \
            f"Y max: expected {expected_ymax}, got {bb.ymax}"
    
        # Volume check:
        # Bulb (cylinder): pi * r^2 * h
        bulb_vol = math.pi * bulb_radius**2 * bulb_height
    
        # Stem (box): stem_width * stem_length * stem_height
        stem_vol = stem_width * stem_length * stem_height
    
        # Overlap region in XY: rectangle [-2,2] x [bulb_radius-overlap, bulb_radius]
        # = [-2,2] x [4, 5], which is fully inside the bulb circle (r=5, half-width=2 < r)
        # For y in [4, 5]: x in [-2,2] is inside circle since sqrt(25-16)=3 > 2
        # So overlap area = stem_width * overlap = 4 * 1 = 4
        # Overlap volume = overlap_area * stem_height (stem is shorter, z=[0,2])
        overlap_area = stem_width * overlap
        overlap_vol  = overlap_area * stem_height
    
        expected_vol = bulb_vol + stem_vol - overlap_vol
        vol = result.val().Volume()
        assert abs(vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {vol:.2f}"
    
        # Check there is exactly 1 solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Check cylindrical face exists (the bulb curved surface)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check a point inside the bulb is inside the solid
        bulb_interior = (0.0, 0.0, bulb_height / 2)
        assert result.val().isInside(bulb_interior), \
            f"Point {bulb_interior} should be inside the solid (bulb region)"
    
        # Check a point inside the stem is inside the solid
        stem_interior = (0.0, stem_center_y, stem_height / 2)
        assert result.val().isInside(stem_interior), \
            f"Point {stem_interior} should be inside the solid (stem region)"
    
        # Check a point outside is not inside
        outside_pt = (bulb_radius + 1, 0.0, bulb_height / 2)
        assert not result.val().isInside(outside_pt), \
            f"Point {outside_pt} should be outside the solid"
    
        # Check that the stem is narrower than the bulb (stem_width < 2*bulb_radius)
        assert stem_width < 2 * bulb_radius, \
            f"Stem width {stem_width} should be less than bulb diameter {2*bulb_radius}"
    
        # Check that the stem is much longer than the bulb diameter (thermometer shape)
        assert stem_length > 5 * 2 * bulb_radius, \
            f"Stem length {stem_length} should be much greater than bulb diameter {2*bulb_radius}"
    
        # Check that bulb extrusion is greater than stem extrusion
        assert bulb_height > stem_height, \
            f"Bulb height {bulb_height} should be greater than stem height {stem_height}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520699/gpt_generated.stl')
