import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. LOAD DATA (LOCAL FILE OR RAW LINK)
# ==========================================
DATA_SOURCE = "category_data_final.csv"
# Example raw GitHub URL:
# DATA_SOURCE = "https://raw.githubusercontent.com/nellgrab/GRB-Interactive-Plot/main/category_data_final.csv"

df = pd.read_csv(DATA_SOURCE)

# Clean numeric columns safely
for col in ["T_90", "L_1998", "z"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df_SN = df[df["KN"].astype(str).str.strip().str.lower() == "no"].copy() if "KN" in df.columns else df.copy()
df_SN_valid = df_SN.copy()
df_SN_valid["nickel mass"] = pd.to_numeric(df_SN_valid["nickel mass"], errors="coerce")
df_SN_valid = df_SN_valid[df_SN_valid["nickel mass"].notna()].copy()

# Fallback if L_frac_1998bw is not separately defined
L_frac_1998bw = df["L_1998"].dropna()

# ==========================================
# 2. COLOUR, SAMPLE & SHAPE MAPPINGS
# ==========================================
size_map = {"bronze": 11, "silver": 12, "gold": 17}
opacity_map = {"gold": 1.0, "silver": 0.65, "bronze": 0.4}

# Plotly marker symbol names matching your Matplotlib shapes:
# 'o' -> 'circle', 'D' -> 'diamond', 'P' -> 'cross' (thick plus)
marker_shape_map = {
    "Collapsar": "circle",
    "S-Merger": "diamond",
    "L-Merger": "diamond",
    "L-Weak": "cross",
    "S-Weak": "cross",
}

progenitors = {
    "Collapsar": ("SN", "#D62728"),
    "S-Merger": ("S-Merger", "#1F77B4"),
    "L-Merger": ("L-Merger", "#2CA02C"),
    "L-Weak": ("L-Weak", "#FF7F0E"),
    "S-Weak": ("S-Weak", "#9467BD"),
}


def hex_to_rgba(hex_color, alpha):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def make_hover_text(subset_df, y_col):
    texts = []
    for _, row in subset_df.iterrows():
        grb = row.get("GRB", "Unknown")
        prog = row.get("progenitor", "N/A")
        sample_tier = row.get("sample", "N/A")
        upper_lim = row.get("upperlimit", "no")

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
            f"<b>Sample:</b> {sample_tier}<br>"
            f"<b>Upper Limit:</b> {upper_lim}<br>"
            f"<b>z:</b> {z_str}<br>"
            f"<b>T_90:</b> {t90_str}<br>"
            f"<b>L_98bw:</b> {l98_str}<br>"
            f"<b>{y_col}:</b> {y_str}"
        )
    return texts


# ==========================================
# 3. INITIALISE 2-PANEL SUBPLOTS
# ==========================================
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.06,
)

# --- Legend Entries (Progenitors, Ancient Host, 1998bw, Sample Tiers) ---
for prog_key, (prog_label, prog_color) in progenitors.items():
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            name=prog_label,
            legendgroup="Progenitors",
            legendgrouptitle_text="<b>Progenitors</b>",
            marker=dict(
                symbol=marker_shape_map.get(prog_key, "circle"),
                size=13,
                color=prog_color,
                line=dict(color=prog_color, width=2),
            ),
            showlegend=True,
            hoverinfo="skip",
        ),
        row=1,
        col=1,
    )

fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        name="Ancient Host",
        legendgroup="Highlights",
        legendgrouptitle_text="<b> Sample</b>",
        marker=dict(
            symbol="circle",
            size=16,
            color="rgba(255, 0, 255, 0.25)",
            line=dict(color="magenta", width=2),
        ),
        showlegend=True,
        hoverinfo="skip",
    ),
    row=1,
    col=1,
)

fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        name="1998bw",
        legendgroup="Highlights",
        marker=dict(
            symbol="star",
            size=18,
            color="rgba(214, 39, 40, 0.45)",
            line=dict(color="#D62728", width=1.5),
        ),
        showlegend=True,
        hoverinfo="skip",
    ),
    row=1,
    col=1,
)

for tier_name, tier_size, tier_alpha in [
    ("Swift: z < 0.3", 17, 1.0),
    ("Swift: z < 0.5", 12, 0.65),
    ("Other: z < 0.5", 11, 0.4),
]:
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            name=tier_name,
            legendgroup="Highlights",
            marker=dict(
                symbol="circle",
                size=tier_size,
                color=f"rgba(128, 128, 128, {tier_alpha})",
                line=dict(color="grey", width=1.5),
            ),
            showlegend=True,
            hoverinfo="skip",
        ),
        row=1,
        col=1,
    )


# ==========================================
# 4. PLOT DATA PANELS
# ==========================================
def add_panel_data(row_idx, y_col, subset_df):
    # Ancient host overlay
    if "ancient" in subset_df.columns:
        anc = subset_df[
            (subset_df["ancient"].astype(str).str.strip().str.lower() == "yes")
            & subset_df["T_90"].notna()
            & subset_df[y_col].notna()
        ]
        if not anc.empty:
            fig.add_trace(
                go.Scatter(
                    x=anc["T_90"],
                    y=anc[y_col],
                    mode="markers",
                    name="Ancient Host",
                    legendgroup="Highlights",
                    showlegend=False,
                    marker=dict(
                        symbol="circle",
                        size=26,
                        color="rgba(255, 0, 255, 0.2)",
                        line=dict(color="magenta", width=1.5),
                    ),
                    text=make_hover_text(anc, y_col),
                    hovertemplate="%{text}<extra></extra>",
                ),
                row=row_idx,
                col=1,
            )

    # Progenitor markers by sample tier
    for prog_key, (_, prog_color) in progenitors.items():
        p_sub = subset_df[
            (subset_df["progenitor"] == prog_key)
            & (subset_df["GRB"].astype(str) != "980425")
            & subset_df["T_90"].notna()
            & subset_df[y_col].notna()
        ].copy()

        if p_sub.empty:
            continue

        p_sub["_tier"] = p_sub["sample"].astype(str).str.strip().str.lower()
        for tier_key, base_size in size_map.items():
            t_sub = p_sub[p_sub["_tier"] == tier_key]
            if t_sub.empty:
                continue

            alpha = opacity_map.get(tier_key, 1.0)
            is_ul = t_sub["upperlimit"].astype(str).str.strip().str.lower().isin(["yes", "true", "1"])
            symbol_vals = ["triangle-down" if ul else marker_shape_map.get(prog_key, "circle") for ul in is_ul]

            fig.add_trace(
                go.Scatter(
                    x=t_sub["T_90"],
                    y=t_sub[y_col],
                    mode="markers",
                    name=prog_key,
                    legendgroup="Progenitors",
                    showlegend=False,
                    marker=dict(
                        symbol=symbol_vals,
                        size=base_size,
                        color=hex_to_rgba(prog_color, alpha),
                        line=dict(color=prog_color, width=2),
                    ),
                    text=make_hover_text(t_sub, y_col),
                    hovertemplate="%{text}<extra></extra>",
                ),
                row=row_idx,
                col=1,
            )

    # Special highlight: GRB 980425
    star_sub = subset_df[
        (subset_df["GRB"].astype(str) == "980425")
        & subset_df["T_90"].notna()
        & subset_df[y_col].notna()
    ]
    if not star_sub.empty:
        fig.add_trace(
            go.Scatter(
                x=star_sub["T_90"],
                y=star_sub[y_col],
                mode="markers",
                name="1998bw",
                legendgroup="Highlights",
                showlegend=False,
                marker=dict(
                    symbol="star",
                    size=24,
                    color="rgba(214, 39, 40, 0.4)",
                    line=dict(color="#D62728", width=1.5),
                ),
                text=make_hover_text(star_sub, y_col),
                hovertemplate="%{text}<extra></extra>",
            ),
            row=row_idx,
            col=1,
        )


add_panel_data(1, "nickel mass", df_SN_valid)
add_panel_data(2, "L_1998", df)

# --- Connecting Dashed Lines for 100316D and 190829A (Bottom Panel) ---
for g1, g2 in [("100316D", "100316D_2"), ("190829A", "190829A_2")]:
    s1 = df[df["GRB"].astype(str) == g1]
    s2 = df[df["GRB"].astype(str) == g2]
    if not s1.empty and not s2.empty:
        x_pair = [s1["T_90"].iloc[0], s2["T_90"].iloc[0]]
        y_pair = [s1["L_1998"].iloc[0], s2["L_1998"].iloc[0]]
        if all(pd.notna(v) for v in x_pair + y_pair):
            fig.add_trace(
                go.Scatter(
                    x=x_pair,
                    y=y_pair,
                    mode="lines",
                    line=dict(color="#D62728", dash="dash", width=2),
                    showlegend=False,
                    hoverinfo="skip",
                ),
                row=2,
                col=1,
            )

# --- 2σ SN Limit Line on Bottom Panel ---
sn_limit = 0.26
fig.add_hline(
    y=sn_limit,
    line=dict(color="black", dash="solid", width=2),
    row=2,
    col=1,
)
fig.add_annotation(
    x=0.02,
    xref="x2 domain",
    y=np.log10(sn_limit * 1.15),
    yref="y2",
    text="<b>2σ SN limit</b>",
    showarrow=False,
    font=dict(color="black", size=14),
    xanchor="left",
)

# ==========================================
# 5. AXES, LOG SCALES, LAYOUT & EXPORT
# ==========================================
fig.update_yaxes(
    title_text="Nickel Mass (M<sub>☉</sub>)",
    type="log",
    dtick=1,
    range=[np.log10(0.001), np.log10(2)],
    title_font=dict(size=18),
    tickfont=dict(size=13),
    showgrid=True,
    row=1,
    col=1,
)

ymin_val = float(L_frac_1998bw.min()) if not L_frac_1998bw.empty else 0.001
ymin_safe = max(ymin_val, 1e-4)
fig.update_yaxes(
    title_text="Luminosity Fraction f<sub>1998bw</sub>",
    type="log",
    dtick=1,
    range=[np.log10(ymin_safe*0.3), np.log10(5)],
    title_font=dict(size=18),
    tickfont=dict(size=13),
    showgrid=True,
    row=2,
    col=1,
)

fig.update_xaxes(
    title_text="Duration T<sub>90</sub> (s)",
    type="log",
    dtick=1,
    title_font=dict(size=18),
    tickfont=dict(size=13),
    showgrid=True,
    row=2,
    col=1,
)
fig.update_xaxes(type="log", showgrid=True, row=1, col=1)

fig.update_layout(
    width=1150,
    height=1150,
    template="plotly_white",
    hovermode="closest",
    legend=dict(
        x=1.02,
        y=0.98,
        xanchor="left",
        yanchor="top",
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="lightgrey",
        borderwidth=1,
        font=dict(size=13),
    ),
)

fig.write_html("interactive_plot_updated.html", include_plotlyjs="cdn")
fig.show(renderer="browser")