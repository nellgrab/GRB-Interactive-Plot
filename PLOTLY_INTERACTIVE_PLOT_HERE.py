#NEWER VERSION USING PLOTLY ! -- WORKS ? 
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. LOAD DATA (FROM A LINK OR LOCAL FILE)
# ==========================================

DATA_SOURCE = "category_data_final.csv"  

df = pd.read_csv(DATA_SOURCE)

df_SN = df[df["KN"] == "no"].copy()  

df_SN_valid = df_SN.copy()
df_SN_valid["nickel mass"] = pd.to_numeric(df_SN_valid["nickel mass"], errors="coerce")  
df_SN_valid = df_SN_valid[df_SN_valid["nickel mass"].notna()].copy()  


df["L_1998"] = pd.to_numeric(df["L_1998"], errors="coerce")  
df["T_90"] = pd.to_numeric(df["T_90"], errors="coerce")  
df["z"] = pd.to_numeric(df["z"], errors="coerce")  


facecolour_map = {"gold": "gold", "silver": "silver", "bronze": "brown"}  
edgecolour_map = {  
    "Collapsar": "red",
    "S-Merger": "blue",
    "L-Merger": "green",
    "L-Weak": "orange",
    "S-Weak": "purple",
}


def make_hover_text(subset_df, y_col):
    """Build hover labels for each row in a subset."""
    texts = []
    for _, row in subset_df.iterrows():
        grb = row.get("GRB", "Unknown")  
        prog = row.get("progenitor", "N/A")  
        z_val = pd.to_numeric(row.get("z", np.nan), errors="coerce")  
        t90_val = pd.to_numeric(row.get("T_90", np.nan), errors="coerce")  
        l98_val = pd.to_numeric(row.get("L_1998", np.nan), errors="coerce")  
        y_val = pd.to_numeric(row.get(y_col, np.nan), errors="coerce")

        z_str = f"{z_val:.2f}" if pd.notna(z_val) else "N/A"
        t90_str = f"{t90_val:.2f}s" if pd.notna(t90_val) else "N/A"
        l98_str = f"{l98_val:.2f}" if pd.notna(l98_val) else "N/A"
        y_str = f"{y_val:.4g}" if pd.notna(y_val) else "N/A"

        texts.append(
            f"<b>GRB:</b> {grb}<br>"
            f"<b>Progenitor:</b> {prog}<br>"
            f"<b>z:</b> {z_str}<br>"
            f"<b>T_90:</b> {t90_str}<br>"
            f"<b>L_98bw:</b> {l98_str}<br>"
            f"<b>{y_col}:</b> {y_str}"
        )
    return texts


# ==========================================
# 2. INITIALISE 2-PANEL SUBPLOTS
# ==========================================
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.06,
)

# --- Plotting Ancient Hosts ---
for row_idx, y_col in [(1, "nickel mass"), (2, "L_1998")]:  #
    if row_idx == 1:
        ancient_subset = df_SN_valid[df_SN_valid["ancient"] == "yes"].copy()  #
    else:
        ancient_subset = df[df["ancient"] == "yes"].copy()  #

    if not ancient_subset.empty:
        valid_mask = ancient_subset[y_col].notna() & ancient_subset["T_90"].notna()  #
        anc_valid = ancient_subset[valid_mask].copy()

        if not anc_valid.empty:
            fig.add_trace(
                go.Scatter(
                    x=anc_valid["T_90"],  #
                    y=anc_valid[y_col],
                    mode="markers",
                    name="Ancient Host",  #
                    legendgroup="Ancient Host",  #
                    showlegend=(row_idx == 1),
                    opacity=0.5,  #
                    marker=dict(
                        symbol="circle",
                        size=24,
                        color="grey",  #
                        line=dict(width=0),
                    ),
                    text=make_hover_text(anc_valid, y_col),
                    hovertemplate="%{text}<extra></extra>",
                ),
                row=row_idx,
                col=1,
            )

# --- Plot Progenitors ---
for progenitor, color in edgecolour_map.items():  #
    sub_ni = df_SN_valid[df_SN_valid["progenitor"] == progenitor]  #
    sub_lum = df[df["progenitor"] == progenitor]  #

    for row_idx, (subset, col_name) in enumerate(
        [(sub_ni, "nickel mass"), (sub_lum, "L_1998")], start=1  #
    ):
        standard_dots = subset[subset["GRB"] != "980425"].copy()  #
        if not standard_dots.empty:
            valid_idx = standard_dots[col_name].notna() & standard_dots["T_90"].notna()  #
            valid_dots = standard_dots[valid_idx].copy()

            if not valid_dots.empty:
                f_colors = [
                    facecolour_map.get(str(s).strip().lower(), "white")  #
                    for s in valid_dots["sample"]  #
                ]
                m_sizes = [
                    15 if str(s).strip().lower() == "gold" else 11  #
                    for s in valid_dots["sample"]  #
                ]

                fig.add_trace(
                    go.Scatter(
                        x=valid_dots["T_90"],  #
                        y=valid_dots[col_name],
                        mode="markers",
                        name=progenitor,
                        legendgroup=progenitor,
                        showlegend=(row_idx == 1),
                        marker=dict(
                            symbol="circle",
                            size=m_sizes,
                            color=f_colors,
                            line=dict(color=color, width=2),  #
                        ),
                        text=make_hover_text(valid_dots, col_name),
                        hovertemplate="%{text}<extra></extra>",
                    ),
                    row=row_idx,
                    col=1,
                )

# --- Plot Special Case: GRB 980425 ---
star_grb = df[df["GRB"] == "980425"].copy()  #
if not star_grb.empty:
    x_val = pd.to_numeric(star_grb["T_90"].iloc[0], errors="coerce")  #
    for row_idx, col_name in [(1, "nickel mass"), (2, "L_1998")]:  #
        y_val = pd.to_numeric(star_grb[col_name].iloc[0], errors="coerce")
        if pd.notna(y_val) and pd.notna(x_val):
            fig.add_trace(
                go.Scatter(
                    x=[x_val],
                    y=[y_val],
                    mode="markers",
                    name="GRB 980425",  #
                    legendgroup="GRB 980425",  #
                    showlegend=(row_idx == 1),
                    marker=dict(
                        symbol="star",  #
                        size=22,
                        color="brown",  #
                        line=dict(color="red", width=1.5),  #
                    ),
                    text=make_hover_text(star_grb.iloc[[0]], col_name),
                    hovertemplate="%{text}<extra></extra>",
                ),
                row=row_idx,
                col=1,
            )

# --- Supernova Limit Line on Bottom Panel ---
sn_limit = 0.13  #
fig.add_hline(
    y=sn_limit,
    line=dict(color="red", dash="dash", width=2),  #
    row=2,
    col=1,
)
fig.add_annotation(
    x=0.02,
    xref="x2 domain",
    y=np.log10(sn_limit * 1.15),
    yref="y2",
    text="<b>Supernova Limit</b>",  #
    showarrow=False,
    font=dict(color="red", size=12),  #
    xanchor="left",
)

# ==========================================
# 3. AXES, LOG SCALES, AND LAYOUT
# ==========================================
fig.update_yaxes(
    title_text="Nickel Mass (M<sub>☉</sub>)",  #
    type="log",
    range=[np.log10(0.001), np.log10(2)],  #
    title_font=dict(size=18),
    tickfont=dict(size=13),
    showgrid=True,
    row=1,
    col=1,
)

fig.update_yaxes(
    title_text="Luminosity Fraction f<sub>1998bw</sub>",  #
    type="log",
    range=[np.log10(0.001), np.log10(5)],  #
    title_font=dict(size=18),
    tickfont=dict(size=13),
    showgrid=True,
    row=2,
    col=1,
)

fig.update_xaxes(
    title_text="T<sub>90</sub> (s)",  #
    type="log",
    title_font=dict(size=18),
    tickfont=dict(size=13),
    showgrid=True,
    row=2,
    col=1,
)
fig.update_xaxes(type="log", showgrid=True, row=1, col=1)

fig.update_layout(
    width=1000,
    height=1150,
    template="plotly_white",
    hovermode="closest",
    legend=dict(
        x=0.01,
        y=0.99,
        xanchor="left",
        yanchor="top",
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="lightgrey",
        borderwidth=1,
        font=dict(size=11),
    ),
)

# Save as a standalone interactive HTML file and open it via a link
fig.write_html("interactive_plot.html", include_plotlyjs="cdn")

# Open interactive plot in browser
fig.show()