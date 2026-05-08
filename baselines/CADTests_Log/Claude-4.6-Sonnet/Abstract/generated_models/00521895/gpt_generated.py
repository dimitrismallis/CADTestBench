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
        box_length = 80.0
        box_width  = 50.0
        box_height = 10.0
    
        cyl_outer_r = 15.0
        cyl_inner_r = 10.0
        cyl_height  = 20.0
    
        # --- Step 1: Create the extruded rectangle (box) ---
        # Box is centered at origin: z from -5 to +5
        result = cq.Workplane("XY").box(box_length, box_width, box_height)
    
        # --- Step 2: Create the outer cylinder on top of the box ---
        # Use circle + extrude so the cylinder sits ON TOP of the box (not centered)
        result = (
            result
            .faces(">Z").workplane()
            .circle(cyl_outer_r)
            .extrude(cyl_height)
        )
    
        # --- Step 3: Cut the inner cylinder to make it hollow ---
        # Cut from the top face of the cylinder downward through the full cylinder height
        result = (
            result
            .faces(">Z").workplane()
            .circle(cyl_inner_r)
            .cutBlind(-cyl_height)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - box_length) < TOL, \
            f"X length: expected {box_length}, got {bb.xlen}"
        assert abs(bb.ylen - box_width) < TOL, \
            f"Y length: expected {box_width}, got {bb.ylen}"
        assert abs(bb.zlen - (box_height + cyl_height)) < TOL, \
            f"Z length: expected {box_height + cyl_height}, got {bb.zlen}"
    
        # Z extents: box centered at origin → zmin = -box_height/2, zmax = box_height/2 + cyl_height
        assert abs(bb.zmin - (-box_height / 2)) < TOL, \
            f"Z min: expected {-box_height/2}, got {bb.zmin}"
        assert abs(bb.zmax - (box_height / 2 + cyl_height)) < TOL, \
            f"Z max: expected {box_height/2 + cyl_height}, got {bb.zmax}"
    
        # Volume check:
        vol_box       = box_length * box_width * box_height
        vol_cyl_outer = math.pi * cyl_outer_r**2 * cyl_height
        vol_cyl_inner = math.pi * cyl_inner_r**2 * cyl_height
        expected_vol  = vol_box + vol_cyl_outer - vol_cyl_inner
        actual_vol    = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Cylindrical faces: outer cylinder wall + inner cylinder wall = 2
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Check the hollow: a point inside the hollow bore should NOT be solid material
        hollow_center_z = box_height / 2 + cyl_height / 2   # midpoint of cylinder height
        point_in_hollow = (0.0, 0.0, hollow_center_z)
        assert not solid.isInside(point_in_hollow), \
            f"Point {point_in_hollow} should be inside the hollow, but isInside returned True"
    
        # Check a point inside the cylinder wall IS solid
        point_in_wall = (cyl_outer_r * 0.8, 0.0, hollow_center_z)
        assert solid.isInside(point_in_wall), \
            f"Point {point_in_wall} should be inside the cylinder wall, but isInside returned False"
    
        # Check a point inside the box IS solid
        point_in_box = (box_length * 0.3, box_width * 0.3, 0.0)
        assert solid.isInside(point_in_box), \
            f"Point {point_in_box} should be inside the box, but isInside returned False"
    
        # Planar faces: at least 6 (bottom, 4 sides, top annular ring)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 6, \
            f"Planar faces: expected at least 6, got {planar_faces}"
    
        print(f"✓ Bounding box: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")
        print(f"✓ Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f} mm³)")
        print(f"✓ Cylindrical faces: {cyl_faces}")
        print(f"✓ Planar faces: {planar_faces}")
        print(f"✓ Hollow cylinder verified (bore interior is not solid material)")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00521895/gpt_generated.stl')
