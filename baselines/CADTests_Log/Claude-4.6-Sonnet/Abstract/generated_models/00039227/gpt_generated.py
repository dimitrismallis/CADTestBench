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
        cyl_radius   = 30.0   # cylinder radius (mm)
        cyl_height   = 20.0   # cylinder height (mm)
        rect_width   = 20.0   # rectangle cutout width (mm)
        rect_height  = 10.0   # rectangle cutout height (mm)
    
        # --- Step 1: Create the base cylinder ---
        result = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # --- Step 2: Cut a rectangular slot through the center of the cylinder ---
        # Select the top face, create a workplane, draw the rectangle, and cut through all
        result = (
            result
            .faces(">Z")
            .workplane()
            .rect(rect_width, rect_height)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # 1. Bounding box: X and Y span should equal the cylinder diameter
        assert abs(bb.xlen - 2 * cyl_radius) < TOL, \
            f"BBox X: expected {2*cyl_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * cyl_radius) < TOL, \
            f"BBox Y: expected {2*cyl_radius}, got {bb.ylen}"
        assert abs(bb.zlen - cyl_height) < TOL, \
            f"BBox Z: expected {cyl_height}, got {bb.zlen}"
    
        # 2. Volume: cylinder volume minus rectangular prism cutout
        cyl_vol  = math.pi * cyl_radius**2 * cyl_height
        rect_vol = rect_width * rect_height * cyl_height
        expected_vol = cyl_vol - rect_vol
        actual_vol   = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical faces: the rectangular cutout is fully inside the cylinder,
        #    so the outer curved surface remains a single unbroken cylindrical face.
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, \
            f"Cylindrical faces: expected 1 (outer curved surface intact), got {cyl_faces}"
    
        # 4. Planar faces:
        #    - Top cap (annular face with rectangular hole) = 1 planar face
        #    - Bottom cap (annular face with rectangular hole) = 1 planar face
        #    - 4 rectangular side walls of the cutout = 4 planar faces
        #    Total = 6 planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 6, \
            f"Planar faces: expected 6 (1 top + 1 bottom + 4 rect walls), got {planar_faces}"
    
        # 5. The rectangular cutout goes all the way through — verify with a ray cast
        #    A point at the center of the cylinder at mid-height should be OUTSIDE (inside the void)
        center_point = (0, 0, 0)
        is_inside = solid.isInside(center_point)
        assert not is_inside, \
            f"Center point should be in the void (outside solid), but isInside returned True"
    
        # 6. A point on the cylinder body (away from the rect cutout) should be inside
        #    Point at 80% of radius along +X, at mid-height — outside the rect cutout region
        body_point = (cyl_radius * 0.8, 0, 0)
        is_body_inside = solid.isInside(body_point)
        assert is_body_inside, \
            f"Body point {body_point} should be inside the solid, but isInside returned False"
    
        # 7. The object should be a single solid (connected body)
        num_solids = result.solids().size()
        assert num_solids == 1, \
            f"Expected 1 solid, got {num_solids}"
    
        # 8. Circular edges: top and bottom rims of the cylinder (2 circles)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 2, \
            f"Circular edges: expected 2 (top and bottom rim), got {circ_edges}"
    
        # 9. Total face count: 1 cylindrical + 6 planar = 7
        total_faces = result.faces().size()
        assert total_faces == 7, \
            f"Total faces: expected 7, got {total_faces}"
    
        print("All assertions passed!")
        print(f"  Cylinder radius:   {cyl_radius} mm")
        print(f"  Cylinder height:   {cyl_height} mm")
        print(f"  Rect cutout:       {rect_width} x {rect_height} mm")
        print(f"  Volume:            {actual_vol:.2f} mm³ (expected {expected_vol:.2f})")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Planar faces:      {planar_faces}")
        print(f"  Total faces:       {total_faces}")
        print(f"  Circular edges:    {circ_edges}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00039227/gpt_generated.stl')
