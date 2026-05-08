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
        # --- Step 1: Create the square base plate 1.5 x 1.5 x 0.0255 ---
        result = cq.Workplane("XY").box(1.5, 1.5, 0.0255)
    
        # --- Step 2: Cut a rectangular hole in the center 0.12 x 0.24 x 0.0255 ---
        # The hole is centered on the plate (default box is centered at origin)
        result = (
            result
            .faces(">Z").workplane()
            .rect(0.12, 0.24)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Check overall bounding box
        # box() is centered at origin by default: Z from -0.01275 to +0.01275
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 1.5) < TOL, f"X length: expected 1.5, got {bb.xlen}"
        assert abs(bb.ylen - 1.5) < TOL, f"Y length: expected 1.5, got {bb.ylen}"
        assert abs(bb.zlen - 0.0255) < TOL, f"Z height: expected 0.0255, got {bb.zlen}"
    
        # Bounding box extents: centered at origin
        assert abs(bb.zmin - (-0.0255 / 2)) < TOL, f"Z min: expected {-0.0255/2}, got {bb.zmin}"
        assert abs(bb.zmax - ( 0.0255 / 2)) < TOL, f"Z max: expected { 0.0255/2}, got {bb.zmax}"
    
        # Check volume: base box minus rectangular cutout
        base_vol = 1.5 * 1.5 * 0.0255
        hole_vol = 0.12 * 0.24 * 0.0255
        expected_vol = base_vol - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check symmetry: center of bounding box should be at (0, 0, 0)
        cob = result.val().CenterOfBoundBox()
        assert abs(cob.x) < TOL, f"BBox Center X: expected 0, got {cob.x}"
        assert abs(cob.y) < TOL, f"BBox Center Y: expected 0, got {cob.y}"
        assert abs(cob.z) < TOL, f"BBox Center Z: expected 0, got {cob.z}"
    
        # The midplane of the box is at z=0
        mid_z = 0.0
    
        # Check that the rectangular hole exists: point at center (0,0,0) is NOT inside the solid
        center_point = (0.0, 0.0, mid_z)
        assert not result.val().isInside(center_point), \
            f"Center point should be inside the hole (not inside solid), but isInside returned True"
    
        # Check that a point away from the hole IS inside the solid
        off_center_point = (0.5, 0.5, mid_z)
        assert result.val().isInside(off_center_point), \
            f"Off-center point should be inside the solid, but isInside returned False"
    
        # Check that there are no cylindrical faces (all planar — rectangular geometry only)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Check face count:
        # OCCT represents top and bottom as single faces with inner hole wires (not split):
        # 1 top face + 1 bottom face + 4 outer side faces + 4 inner hole wall faces = 10
        face_count = result.faces().size()
        assert face_count == 10, f"Expected 10 planar faces, got {face_count}"
    
        # |Z selects faces whose normal is parallel to Z (top and bottom faces) = 2
        z_normal_faces = result.faces("|Z").size()
        assert z_normal_faces == 2, \
            f"Expected 2 faces with normal parallel to Z (top + bottom), got {z_normal_faces}"
    
        # #Z selects faces whose normal is perpendicular to Z (vertical side walls)
        # 4 outer side faces + 4 inner hole wall faces = 8
        z_perp_faces = result.faces("#Z").size()
        assert z_perp_faces == 8, \
            f"Expected 8 faces perpendicular to Z (4 outer + 4 inner), got {z_perp_faces}"
    
        # Verify the hole: a vertical line through the center should intersect 0 solid faces
        # (the line passes through the hole, not through material)
        intersected = result.val().facesIntersectedByLine((0, 0, -1), (0, 0, 1))
        assert len(intersected) == 0, \
            f"Line through center (hole) should intersect 0 faces, got {len(intersected)}"
    
        # Verify hole dimensions via isInside checks at mid_z
        # Hole is 0.12 wide (X) x 0.24 tall (Y), centered at origin
        # Point at (0.05, 0.0, mid_z) — inside the hole (half-width in X = 0.06)
        inside_hole = (0.05, 0.0, mid_z)
        assert not result.val().isInside(inside_hole), \
            f"Point inside hole should not be in solid, but isInside returned True"
    
        # Point just outside the hole boundary in X IS in the solid
        # hole half-width in X = 0.06, so x=0.07 should be in solid
        outside_hole_x = (0.07, 0.0, mid_z)
        assert result.val().isInside(outside_hole_x), \
            f"Point just outside hole (x=0.07) should be in solid, but isInside returned False"
    
        # Point just outside the hole boundary in Y IS in the solid
        # hole half-width in Y = 0.12, so y=0.13 should be in solid
        outside_hole_y = (0.0, 0.13, mid_z)
        assert result.val().isInside(outside_hole_y), \
            f"Point just outside hole (y=0.13) should be in solid, but isInside returned False"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00037161/gpt_generated.stl')
