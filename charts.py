"""
charts.py — colourful, professional Plotly chart builders.

Every function returns a Plotly figure styled with a consistent theme and
palette. If Plotly is not installed, HAS_PLOTLY is False and the app falls
back to Streamlit's built-in charts automatically.
"""

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except Exception:  # pragma: no cover
    HAS_PLOTLY = False

# ------------------------------------------------------------------ palette
PALETTE = [
    "#10B981", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6",
    "#EC4899", "#14B8A6", "#F97316", "#6366F1", "#84CC16",
]
STATUS_COLORS = {"Completed": "#10B981", "Pending": "#F59E0B", "Cancelled": "#EF4444"}
FOOD_COLORS = {"Vegetarian": "#10B981", "Vegan": "#84CC16", "Non-Vegetarian": "#EF4444"}
MEAL_COLORS = {"Breakfast": "#F59E0B", "Lunch": "#3B82F6", "Dinner": "#8B5CF6", "Snacks": "#EC4899"}

FONT = "Inter, system-ui, -apple-system, Segoe UI, sans-serif"


def _rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _style(fig, title, height):
    fig.update_layout(
        title=dict(text=title, x=0.0, xanchor="left",
                   font=dict(size=17, color="#0F172A", family=FONT)),
        template="plotly_white",
        height=height,
        margin=dict(l=10, r=14, t=50, b=10),
        font=dict(family=FONT, size=13, color="#334155"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(font_size=13, font_family=FONT),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EEF2F7", zeroline=False)
    return fig


# ------------------------------------------------------------------ charts
def bar(series, title, horizontal=False, color_map=None, height=360,
        x_title="", y_title=""):
    df = series.reset_index()
    df.columns = ["category", "value"]
    df["category"] = df["category"].astype(str)

    kw = dict(text="value")
    if color_map:
        kw.update(color="category", color_discrete_map=color_map)
    else:
        kw.update(color="category", color_discrete_sequence=PALETTE)

    if horizontal:
        df = df.iloc[::-1]
        fig = px.bar(df, x="value", y="category", orientation="h", **kw)
        fig.update_traces(textposition="outside", cliponaxis=False)
    else:
        fig = px.bar(df, x="category", y="value", **kw)
        fig.update_traces(textposition="outside", cliponaxis=False)

    _style(fig, title, height)
    fig.update_layout(showlegend=False, xaxis_title=x_title, yaxis_title=y_title)
    return fig


def donut(series, title, color_map=None, height=360):
    df = series.reset_index()
    df.columns = ["category", "value"]
    df["category"] = df["category"].astype(str)

    fig = px.pie(
        df, names="category", values="value", hole=0.58,
        color="category" if color_map else None,
        color_discrete_map=color_map,
        color_discrete_sequence=PALETTE,
    )
    fig.update_traces(
        textposition="inside", textinfo="percent+label",
        marker=dict(line=dict(color="#FFFFFF", width=2)),
    )
    _style(fig, title, height)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.12))
    return fig


def grouped_bar(pivot, title, x_title="", y_title="", height=400):
    idx = pivot.index.name or "index"
    df = pivot.reset_index().melt(id_vars=idx, var_name="group", value_name="value")
    df[idx] = df[idx].astype(str)
    fig = px.bar(df, x=idx, y="value", color="group", barmode="group",
                 color_discrete_sequence=PALETTE)
    _style(fig, title, height)
    fig.update_layout(xaxis_title=x_title, yaxis_title=y_title, legend_title="")
    return fig


def area(series, title, color="#3B82F6", height=340):
    df = series.reset_index()
    df.columns = ["x", "y"]
    fig = px.area(df, x="x", y="y")
    fig.update_traces(line=dict(color=color, width=2.6),
                      fillcolor=_rgba(color, 0.16))
    _style(fig, title, height)
    fig.update_layout(xaxis_title="", yaxis_title="")
    return fig
