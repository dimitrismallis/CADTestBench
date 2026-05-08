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
        # Units: user gave meters; CadQuery defaults to mm, so convert m -> mm
        m_to_mm = 1000.0
    
        # --- Given dimensions (meters) ---
        col_len_m = 0.05      # along Y
        col_w_m   = 0.35      # along X (columns slightly larger than horizontal section)
        beam_len_m = 1.175    # along X
        beam_w_m   = 0.35     # along Y
    
        col_h_m  = 0.725
        beam_h_m = 0.025
    
        # --- Convert to mm ---
        col_len = col_len_m * m_to_mm
        col_w   = col_w_m * m_to_mm
        beam_len = beam_len_m * m_to_mm
        beam_w   = beam_w_m * m_to_mm
    
        col_h  = col_h_m * m_to_mm
        beam_h = beam_h_m * m_to_mm
    
        # Make columns "slightly larger width than the horizontal section" in X
        # (beam width in X is its thickness; for a rectangle, X dimension is "length" here)
        # We'll reduce the beam's X thickness slightly relative to column width.
        beam_thickness_x = col_w * 0.92  # 8% narrower than columns
    
        # Place the beam centered at Y=0, and columns below it (negative Y),
        # so the footprint looks like a U open toward -Y.
        # Beam spans in X: beam_len, in Y: beam_w
        # Columns: in X: col_w, in Y: col_len
        y_beam_center = 0.0
        y_col_center = -(beam_w / 2.0 + col_len / 2.0)
    
        # Column centers in X at the ends of the beam
        x_left_col = -(beam_len / 2.0) + (col_w / 2.0)
        x_right_col = (beam_len / 2.0) - (col_w / 2.0)
    
        # --- Build solids ---
        # 1) Beam: thin extrusion
        beam = (
            cq.Workplane("XY")
            .center(0, y_beam_center)
            .rect(beam_len, beam_w)
            .extrude(beam_h)
        )
    
        # 2) Columns: tall extrusions, fused to beam
        cols = (
            cq.Workplane("XY")
            .pushPoints([(x_left_col, y_col_center), (x_right_col, y_col_center)])
            .rect(col_w, col_len)
            .extrude(col_h)
        )
    
        # 3) Add a slight narrowing of the beam in X by cutting its sides (optional but matches "columns wider")
        #    We already made beam_thickness_x narrower by using beam_len as span and beam_w as depth;
        #    to reflect "width" difference in X, we can trim beam in X to beam_thickness_x around its center.
        #    However, beam_len is the span; the "width" difference is better represented as beam thickness in X.
        #    So we cut the beam to a narrower X thickness while keeping the overall span via columns.
        #    Implement as: cut two side slabs from the beam, leaving a central strip of thickness beam_thickness_x.
        side_cut = (
            cq.Workplane("XY")
            .center(0, y_beam_center)
            .rect(beam_len, beam_w)
            .extrude(beam_h)
            .cut(
                cq.Workplane("XY")
                .center(0, y_beam_center)
                .rect(beam_thickness_x, beam_w)
                .extrude(beam_h)
            )
        )
        # side_cut is the material to remove from the beam
        beam = beam.cut(side_cut)
    
        # Final: union beam + columns
        result = cols.union(beam)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00985066/gpt_generated.stl')
