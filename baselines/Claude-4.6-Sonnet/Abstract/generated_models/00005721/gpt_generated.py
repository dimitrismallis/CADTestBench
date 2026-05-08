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
        # --- Step 1: Define obtuse scalene triangle vertices ---
        # Vertices chosen so that:
        #   - All three sides have different lengths (scalene)
        #   - One interior angle is > 90° (obtuse)
        # A = (0, 0), B = (10, 0), C = (2, 3)
        # Side AB = 10
        # Side AC = sqrt(4 + 9) = sqrt(13) ≈ 3.606
        # Side BC = sqrt(64 + 9) = sqrt(73) ≈ 8.544
        # Angle at C (between AC and BC):
        #   cos(C) = (AC² + BC² - AB²) / (2·AC·BC)
        #           = (13 + 73 - 100) / (2·sqrt(13)·sqrt(73))
        #           = -14 / (2·sqrt(949)) ≈ -0.227  → angle ≈ 103.1° (obtuse) ✓
        # All sides different → scalene ✓
    
        A = (0.0, 0.0)
        B = (10.0, 0.0)
        C = (2.0, 3.0)
        thickness = 2.0  # extrusion thickness in Z
    
        # --- Step 2: Build the triangle profile as a closed wire and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(A[0], A[1])
            .lineTo(B[0], B[1])
            .lineTo(C[0], C[1])
            .close()
            .extrude(thickness)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
    
        # Bounding box checks
        bb = solid.BoundingBox()
        assert abs(bb.xmin - 0.0) < TOL, f"xmin expected 0.0, got {bb.xmin}"
        assert abs(bb.xmax - 10.0) < TOL, f"xmax expected 10.0, got {bb.xmax}"
        assert abs(bb.ymin - 0.0) < TOL, f"ymin expected 0.0, got {bb.ymin}"
        assert abs(bb.ymax - 3.0) < TOL, f"ymax expected 3.0, got {bb.ymax}"
        assert abs(bb.zmin - 0.0) < TOL, f"zmin expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - thickness) < TOL, f"zmax expected {thickness}, got {bb.zmax}"
    
        # Volume check: area of triangle × thickness
        # Triangle area = 0.5 * |AB × AC| = 0.5 * |(10,0) × (2,3)| = 0.5 * |30 - 0| = 15
        triangle_area = 0.5 * abs((B[0] - A[0]) * (C[1] - A[1]) - (C[0] - A[0]) * (B[1] - A[1]))
        expected_volume = triangle_area * thickness
        actual_volume = solid.Volume()
        assert abs(actual_volume - expected_volume) < TOL, \
            f"Volume expected {expected_volume:.4f}, got {actual_volume:.4f}"
    
        # Face count: a triangular prism has 5 faces
        # (2 triangular faces top/bottom + 3 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 5, f"Face count expected 5, got {face_count}"
    
        # Edge count: a triangular prism has 9 edges
        edge_count = result.edges().size()
        assert edge_count == 9, f"Edge count expected 9, got {edge_count}"
    
        # Vertex count: a triangular prism has 6 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 6, f"Vertex count expected 6, got {vertex_count}"
    
        # Verify scalene: all three side lengths are different
        AB = math.sqrt((B[0]-A[0])**2 + (B[1]-A[1])**2)
        AC = math.sqrt((C[0]-A[0])**2 + (C[1]-A[1])**2)
        BC = math.sqrt((C[0]-B[0])**2 + (C[1]-B[1])**2)
        assert abs(AB - AC) > TOL, f"Scalene check failed: AB={AB:.4f} == AC={AC:.4f}"
        assert abs(AB - BC) > TOL, f"Scalene check failed: AB={AB:.4f} == BC={BC:.4f}"
        assert abs(AC - BC) > TOL, f"Scalene check failed: AC={AC:.4f} == BC={BC:.4f}"
    
        # Verify obtuse: one angle > 90° (cos < 0)
        # Angle at A: between AB and AC
        cos_A = ((B[0]-A[0])*(C[0]-A[0]) + (B[1]-A[1])*(C[1]-A[1])) / (AB * AC)
        # Angle at B: between BA and BC
        cos_B = ((A[0]-B[0])*(C[0]-B[0]) + (A[1]-B[1])*(C[1]-B[1])) / (AB * BC)
        # Angle at C: between CA and CB
        cos_C = ((A[0]-C[0])*(B[0]-C[0]) + (A[1]-C[1])*(B[1]-C[1])) / (AC * BC)
    
        angles_deg = [math.degrees(math.acos(cos_A)),
                      math.degrees(math.acos(cos_B)),
                      math.degrees(math.acos(cos_C))]
        print(f"Triangle angles: A={angles_deg[0]:.2f}°, B={angles_deg[1]:.2f}°, C={angles_deg[2]:.2f}°")
        print(f"Side lengths: AB={AB:.4f}, AC={AC:.4f}, BC={BC:.4f}")
        print(f"Volume: {actual_volume:.4f}")
    
        obtuse_count = sum(1 for a in angles_deg if a > 90.0)
        assert obtuse_count == 1, \
            f"Expected exactly 1 obtuse angle, got {obtuse_count}. Angles: {angles_deg}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00005721/gpt_generated.stl')
