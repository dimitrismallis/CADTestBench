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
        outer_radius = 20.0   # mm
        inner_radius = 5.0    # mm (small)
        height       = 150.0  # mm (long)
    
        # --- Step 1: Create outer solid cylinder ---
        result = cq.Workplane("XY").cylinder(height, outer_radius)
    
        # --- Step 2: Cut inner cylinder to make it hollow ---
        result = result.faces(">Z").workplane().circle(inner_radius).cutThruAll()
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 2 * outer_radius) < TOL, \
            f"X extent: expected {2*outer_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * outer_radius) < TOL, \
            f"Y extent: expected {2*outer_radius}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Height (Z): expected {height}, got {bb.zlen}"
    
        # Check volume: pi * (R_outer^2 - R_inner^2) * height
        expected_vol = math.pi * (outer_radius**2 - inner_radius**2) * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check cylindrical faces: outer surface + inner surface = 2 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2 (outer + inner), got {cyl_faces}"
    
        # Check planar faces: top and bottom flat annular faces = 2
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, \
            f"Planar faces: expected 2 (top + bottom), got {planar_faces}"
    
        # Check total face count: 2 cylindrical + 2 planar = 4
        total_faces = result.faces().size()
        assert total_faces == 4, \
            f"Total faces: expected 4, got {total_faces}"
    
        # Check circular edges: 4 circles (top outer, top inner, bottom outer, bottom inner)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 4, \
            f"Circular edges: expected 4, got {circ_edges}"
    
        # Check the bore center is hollow: a point at the axis center should be outside the solid
        bore_center = (0, 0, 0)
        assert not result.val().isInside(bore_center), \
            "Bore center (0,0,0) should be outside the solid (hollow), but isInside returned True"
    
        # Check a point inside the wall material is inside the solid
        wall_mid_r = (inner_radius + outer_radius) / 2.0  # midpoint of wall thickness
        wall_point = (wall_mid_r, 0, 0)
        assert result.val().isInside(wall_point), \
            f"Wall midpoint {wall_point} should be inside the solid material"
    
        # Check a point outside the outer radius is outside the solid
        outside_point = (outer_radius + 5.0, 0, 0)
        assert not result.val().isInside(outside_point), \
            f"Point {outside_point} beyond outer radius should be outside the solid"
    
        # Verify the hole goes all the way through:
        # A ray through the wall (not the bore) along Z should intersect top and bottom planar faces
        wall_ray_origin = (wall_mid_r, 0, -height)  # start below the cylinder, in the wall region
        faces_along_z = result.val().facesIntersectedByLine(wall_ray_origin, (0, 0, 1))
        assert len(faces_along_z) == 2, \
            f"Ray through wall along Z should intersect 2 faces (top+bottom annuli), got {len(faces_along_z)}"
    
        # Center of mass should be at the geometric center (0, 0, 0) due to symmetry
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X should be ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z should be ~0, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00004596/gpt_generated.stl')
