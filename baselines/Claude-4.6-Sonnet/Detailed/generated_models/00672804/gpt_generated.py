import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Draw a 1.5 x 1.5 square and extrude to height 0.1125 ---
        result = (
            cq.Workplane("XY")
            .rect(1.5, 1.5)
            .extrude(0.1125)
        )
    
        # --- Step 2: Create a centered hole with diameter 0.15 (radius 0.075) ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .hole(0.15)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Check overall bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 1.5) < TOL, f"X length: expected 1.5, got {bb.xlen}"
        assert abs(bb.ylen - 1.5) < TOL, f"Y length: expected 1.5, got {bb.ylen}"
        assert abs(bb.zlen - 0.1125) < TOL, f"Z height: expected 0.1125, got {bb.zlen}"
    
        # Check bounding box extents are centered at origin in X and Y
        assert abs(bb.xmin + 0.75) < TOL, f"xmin: expected -0.75, got {bb.xmin}"
        assert abs(bb.xmax - 0.75) < TOL, f"xmax: expected 0.75, got {bb.xmax}"
        assert abs(bb.ymin + 0.75) < TOL, f"ymin: expected -0.75, got {bb.ymin}"
        assert abs(bb.ymax - 0.75) < TOL, f"ymax: expected 0.75, got {bb.ymax}"
        assert abs(bb.zmin) < TOL, f"zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - 0.1125) < TOL, f"zmax: expected 0.1125, got {bb.zmax}"
    
        # Check volume: box volume minus cylinder hole volume
        box_vol = 1.5 * 1.5 * 0.1125
        hole_vol = math.pi * (0.075 ** 2) * 0.1125
        expected_vol = box_vol - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that there is exactly 1 cylindrical face (the hole wall)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check planar faces:
        # 4 side faces + 1 top face (annular) + 1 bottom face (annular) = 6 planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 6, f"Planar faces: expected 6, got {planar_faces}"
    
        # Check total face count: 6 planar + 1 cylindrical = 7
        total_faces = result.faces().size()
        assert total_faces == 7, f"Total faces: expected 7, got {total_faces}"
    
        # Check that the hole passes through the center — center point should NOT be inside solid
        center_point = (0.0, 0.0, 0.05)
        is_inside = result.val().isInside(center_point)
        assert not is_inside, f"Center of hole should be outside (hollow), but isInside returned {is_inside}"
    
        # Check that a point just outside the hole radius IS inside the solid
        # 0.1 > 0.075 radius, so this point should be inside the solid
        near_hole_point = (0.1, 0.0, 0.05)
        is_inside_solid = result.val().isInside(near_hole_point)
        assert is_inside_solid, f"Point near hole but inside solid should be inside, got {is_inside_solid}"
    
        # Check circular edges: 2 circular edges (top rim and bottom rim of hole)
        circular_edges = result.edges("%Circle").size()
        assert circular_edges == 2, f"Circular edges: expected 2, got {circular_edges}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Planar faces: {planar_faces}")
        print(f"  Total faces: {total_faces}")
        print(f"  Circular edges: {circular_edges}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00672804/gpt_generated.stl')
