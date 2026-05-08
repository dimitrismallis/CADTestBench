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
        base = 60.0       # parallelogram base width
        pg_height = 40.0  # parallelogram height (Y extent)
        shear = 20.0      # horizontal shear offset at top
        extrude_h = 15.0  # extrusion height (Z)
        sq_side = 20.0    # square hole side length
    
        # Parallelogram vertices (counter-clockwise):
        # (0,0) -> (60,0) -> (80,40) -> (20,40)
        # Centroid: x=(0+60+80+20)/4=40, y=(0+0+40+40)/4=20
        cx = (0 + base + base + shear + shear) / 4  # = 40
        cy = pg_height / 2                            # = 20
    
        # --- Step 1: Sketch and extrude the parallelogram ---
        parallelogram = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(base, 0)
            .lineTo(base + shear, pg_height)
            .lineTo(shear, pg_height)
            .close()
            .extrude(extrude_h)
        )
    
        # --- Step 2 & 3: Draw a square centered at the parallelogram centroid
        #     on the top face, then cut through all ---
        result = (
            parallelogram
            .faces(">Z")
            .workplane()
            .center(cx, cy)
            .rect(sq_side, sq_side)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xmin - 0) < TOL, f"xmin expected 0, got {bb.xmin}"
        assert abs(bb.xmax - (base + shear)) < TOL, f"xmax expected {base+shear}, got {bb.xmax}"
        assert abs(bb.ymin - 0) < TOL, f"ymin expected 0, got {bb.ymin}"
        assert abs(bb.ymax - pg_height) < TOL, f"ymax expected {pg_height}, got {bb.ymax}"
        assert abs(bb.zmin - 0) < TOL, f"zmin expected 0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_h) < TOL, f"zmax expected {extrude_h}, got {bb.zmax}"
    
        # Volume check:
        # Parallelogram area = base * height = 60 * 40 = 2400 mm²
        # Square hole area = 20 * 20 = 400 mm²
        # Net area = 2400 - 400 = 2000 mm²
        # Volume = net_area * extrude_h = 2000 * 15 = 30000 mm³
        pg_area = base * pg_height
        sq_area = sq_side * sq_side
        expected_vol = (pg_area - sq_area) * extrude_h
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Check that the square hole exists: a point inside the hole region
        # should NOT be inside the solid
        hole_center = (cx, cy, extrude_h / 2)
        assert not result.val().isInside(hole_center), \
            f"Point {hole_center} should be inside the hole (not solid), but isInside returned True"
    
        # Check that a point clearly inside the solid IS inside
        # Near bottom-left of parallelogram, well away from the hole
        solid_point = (5.0, 5.0, extrude_h / 2)
        assert result.val().isInside(solid_point), \
            f"Point {solid_point} should be inside the solid, but isInside returned False"
    
        # No cylindrical faces — all cuts are planar (square hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Count planar faces — should be at least 8
        # (2 top/bottom + 4 outer sides + 4 inner hole walls, some may be merged by OCCT)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 8, f"Expected at least 8 planar faces, got {planar_faces}"
        print(f"Planar face count: {planar_faces}")
    
        # Verify the hole goes all the way through:
        # A vertical line through the hole center should intersect 0 faces
        # (the hole is open — no horizontal face blocks it)
        intersected_hole = result.val().facesIntersectedByLine(
            (cx, cy, -1), (0, 0, 1)
        )
        assert len(intersected_hole) == 0, \
            f"Line through hole center should intersect 0 faces (open hole), got {len(intersected_hole)}"
    
        # A vertical line through a solid point should intersect 2 faces (top and bottom)
        solid_x, solid_y = 5.0, 5.0
        intersected_solid = result.val().facesIntersectedByLine(
            (solid_x, solid_y, -1), (0, 0, 1)
        )
        assert len(intersected_solid) == 2, \
            f"Line through solid point should intersect 2 faces (top+bottom), got {len(intersected_solid)}"
    
        # Verify edges parallel to Z: 4 outer corners + 4 inner hole corners = 8
        z_edges = result.edges("|Z").size()
        print(f"Edges parallel to Z: {z_edges}")
        assert z_edges == 8, f"Expected 8 vertical edges (4 outer + 4 inner), got {z_edges}"
    
        # Verify circular edges count = 0 (square hole, no circles)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 0, f"Expected 0 circular edges, got {circ_edges}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00039365/gpt_generated.stl')
