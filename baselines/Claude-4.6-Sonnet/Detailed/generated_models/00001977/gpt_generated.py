import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        base = 0.20312
        height = 0.20312
        extrusion = 0.75
    
        # --- Step 1: Create right triangle profile and extrude ---
        # Right triangle with vertices at (0,0), (base,0), (0,height)
        # Using lineTo to draw the profile, then close
        result = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(base, 0)
            .lineTo(0, height)
            .close()
            .extrude(extrusion)
        )
    
        # --- Step 2: Rotate -90 degrees around Y-axis ---
        # rotate(axisStartPoint, axisEndPoint, angleDegrees)
        result = result.rotate((0, 0, 0), (0, 1, 0), -90)
    
        # --- Final object verification ---
        TOL = 0.001
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # After -90° rotation around Y: (x,y,z) -> (z, y, -x)
        # Original: x in [0, base], y in [0, height], z in [0, extrusion]
        # New: x in [0, extrusion], y in [0, height], z in [-base, 0]
        expected_xlen = extrusion   # 0.75
        expected_ylen = height      # 0.20312
        expected_zlen = base        # 0.20312
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume: triangle area * extrusion = 0.5 * base * height * extrusion
        expected_vol = 0.5 * base * height * extrusion
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: triangular prism has 5 faces
        # 2 triangular faces + 3 rectangular faces
        face_count = result.faces().size()
        assert face_count == 5, f"Face count: expected 5, got {face_count}"
    
        # Check planar faces (all 5 should be planar for a prism)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 5, f"Planar face count: expected 5, got {planar_count}"
    
        # Edge count: triangular prism has 9 edges
        edge_count = result.edges().size()
        assert edge_count == 9, f"Edge count: expected 9, got {edge_count}"
    
        # Vertex count: triangular prism has 6 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 6, f"Vertex count: expected 6, got {vertex_count}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: x={bb.xlen:.5f}, y={bb.ylen:.5f}, z={bb.zlen:.5f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00001977/gpt_generated.stl')
