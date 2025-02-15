import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

MAX_STREAMLIT_SLIDER_VALUE = (1 << 53) - 1  # Max allowed by Streamlit


def get_page(df,
             x_axis=None,
             y_axes=None,
             x_log=False,
             y_log=False,
             plot_types=None,
             plot_colors=None,
             sort_column=None,
             sort_order="Ascending",
             enable_filter=False,
             enable_bubble_size=False,
             bubble_column=None,
             enable_ref_line=False,
             ref_value=None,
             ref_color=None,
             filter_column=None,
             filter_range=None):
    st.subheader("📊 Explore Data with Custom Plotly")

    # Sidebar options
    st.sidebar.header("Graph Settings")

    x_axis = st.sidebar.selectbox(
        "Select X-axis",
        df.columns,
        index=df.columns.get_loc(x_axis) if x_axis in df.columns else 0
    )

    y_axes = determine_y_axes(df, y_axes)

    is_y_categorical = any(pd.api.types.is_object_dtype(df[y]) or pd.api.types.is_string_dtype(df[y]) for y in y_axes)

    x_log = st.sidebar.checkbox("Log Scale for X-axis",
                                disabled=not pd.api.types.is_numeric_dtype(df[x_axis]),
                                value=x_log)
    y_log = st.sidebar.checkbox("Log Scale for Y-axis", disabled=is_y_categorical,
                                value=y_log if is_y_categorical else y_log)

    st.sidebar.subheader("Sorting Options")
    sort_column = st.sidebar.selectbox("Select Column to Sort", df.columns,
                                       index=df.columns.get_loc(sort_column) if sort_column in df.columns else 0)
    sort_order = st.sidebar.radio("Sort Order", ["Ascending", "Descending"],
                                  index=0 if sort_order == "Ascending" else 1)
    df = df.sort_values(by=sort_column, ascending=(sort_order == "Ascending")).reset_index(drop=True)

    st.sidebar.subheader("Filtering Options")
    enable_filter = st.sidebar.checkbox("Enable Filtering", value=enable_filter)

    if enable_filter:
        df = filter_sub_selection(df, filter_column, filter_range)
        if df.empty:
            st.warning("⚠️ The selected filter range resulted in no data. Please adjust the filter criteria.")
            return

    st.sidebar.subheader("Chart type config")
    enable_color_mode = st.sidebar.checkbox("Enable Color Mode")

    color_mode_columns = determine_color_mode_columns(df, enable_color_mode)

    plot_colors, plot_types = determine_sub_plots(enable_color_mode, plot_colors, plot_types, y_axes)

    enable_bubble_size = st.sidebar.checkbox("Enable Bubble Size", True if enable_bubble_size else None)

    bubble_column, log_scale_factor = determine_bubble_size(bubble_column, df, enable_bubble_size)

    enable_ref_line = st.sidebar.checkbox("Enable Reference Line", True if enable_ref_line else None)
    ref_value = st.sidebar.number_input("Reference Line Value",
                                        ref_value if ref_value else 0) if enable_ref_line else None
    ref_color = st.sidebar.color_picker("Reference Line Color",
                                        ref_color if ref_color else "#FF0000") if enable_ref_line else None

    df = update_x_axis_to_category(df, x_axis)

    # **Hover Info: Now enabled by default with X and selected Y columns**
    default_hover_columns = [x_axis] + y_axes
    enable_hover = st.sidebar.checkbox("Enable Hover Info", value=True)  # Default to True
    hover_columns = st.sidebar.multiselect("Select Hover Columns", df.columns,
                                           default=default_hover_columns) if enable_hover else []

    # Function to format hover text properly
    def format_hover_text(row):
        return "<br>".join([f"{col}: {row[col]}" for col in hover_columns])

    # Create hover text column
    df["hover_text"] = df.apply(format_hover_text, axis=1) if enable_hover and hover_columns else None

    # Get optimized tick values for log scale
    x_ticks = limit_tick_values(df[x_axis].unique()) if x_log and pd.api.types.is_numeric_dtype(df[x_axis]) else None
    y_ticks = limit_tick_values(np.unique(df[y_axes].values)) if y_log else None

    fig = go.Figure()

    for y in y_axes:
        color_args = {"color": color_mode_columns} if enable_color_mode else {
            "color_discrete_sequence": [plot_colors[y]]}
        hover_args = {"hover_data": hover_columns} if enable_hover else {"hover_data": None}

        if plot_types[y] == "Line":
            traces = px.line(df, x=x_axis, y=y, **color_args, **hover_args)
        elif plot_types[y] == "Scatter":
            traces = px.scatter(df,
                                x=x_axis,
                                y=y,
                                size="bubble_size" if enable_bubble_size else None,
                                size_max=30 if enable_bubble_size else None,  # Increase max bubble size (default is 20)
                                **color_args,
                                **hover_args)

            # Set fixed size bubbles
            if not enable_bubble_size:
                traces.update_traces(
                    marker=dict(
                        opacity=0.7,
                        size=10,
                        line=dict(width=1, color='white')
                    )
                )

            traces.update_traces(
                marker=dict(
                    opacity=0.7,
                    line=dict(width=1, color='white')
                )
            )

        elif plot_types[y] == "Bar":
            traces = px.bar(df, x=x_axis, y=y, **color_args, **hover_args)

        # Add each trace from the generated px figure to the main figure
        for trace in traces.data:
            fig.add_trace(trace)

    add_bubble_size_legend(bubble_column, df, enable_bubble_size, fig, log_scale_factor)

    add_ref_line(enable_ref_line, fig, ref_color, ref_value)

    fig.update_layout(
        xaxis=dict(
            type="log" if x_log and pd.api.types.is_numeric_dtype(df[x_axis]) else "category",
            categoryorder="array",
            categoryarray=df[x_axis] if pd.api.types.is_numeric_dtype(df[x_axis]) else None,
            tickvals=x_ticks if x_log else None,  # Use real values for tick marks
            tickmode="array" if x_log else None,
            showgrid=True,
        ),
        yaxis=dict(
            type="log" if y_log else "linear",
            tickvals=y_ticks if y_log else None,  # Use real values for tick marks
            tickmode="array" if y_log else None,
        ),
        xaxis_title=x_axis,
        yaxis_title=','.join(y_axes),
        title=f"Customized Graph X: {x_axis} vs Y: {', '.join(y_axes)}",
        height=800
    )

    st.plotly_chart(fig)


def update_x_axis_to_category(df, x_axis):
    if pd.api.types.is_object_dtype(df[x_axis]):
        df[x_axis] = df[x_axis].astype(str)
    return df


def determine_bubble_size(bubble_column, df, enable_bubble_size):
    log_scale_factor = 1
    if enable_bubble_size:
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        bubble_column = st.sidebar.selectbox("Select Bubble Size Column", numeric_columns, index=numeric_columns.index(
            bubble_column) if bubble_column in numeric_columns else 0)
        log_scale_factor = st.sidebar.slider("Bubble Size Log Scale Factor", 1.0, 10.0, 5.0, step=0.1)
        df["bubble_size"] = np.clip((np.log1p(df[bubble_column])) * log_scale_factor, 1, 30)
    return bubble_column, log_scale_factor


def determine_color_mode_columns(df, enable_color_mode):
    color_mode_columns = None
    if enable_color_mode:
        color_mode_columns = st.sidebar.selectbox("Select Color Mode Column",
                                                  df.select_dtypes(exclude=[np.number]).columns, index=0)
    return color_mode_columns


def determine_y_axes(df, y_axes):
    if y_axes:
        default = [y for y in y_axes if y in df.columns]
    else:
        default = [df.columns[1]]
    y_axes = st.sidebar.multiselect("Select Y-axis", df.columns, default=default)
    return y_axes


def add_bubble_size_legend(bubble_column, df, enable_bubble_size, fig, log_scale_factor):
    # Add Bubble Size Legend (Only if Scatter is selected)
    if enable_bubble_size:
        example_sizes = [min(df[bubble_column]), np.median(df[bubble_column]), max(df[bubble_column])]
        for size in example_sizes:
            fig.add_trace(go.Scatter(
                x=[None], y=[None],  # Hidden data points
                mode="markers",
                marker=dict(size=np.log1p(size) * log_scale_factor, color="gray", opacity=0.5),
                name=f"{bubble_column}: {round(size)}"
            ))


def add_ref_line(enable_ref_line, fig, ref_color, ref_value):
    if enable_ref_line:
        fig.add_hline(y=ref_value, line_dash="dash", line_color=ref_color, annotation_text=f"Ref: {ref_value}")


def determine_sub_plots(enable_color_mode, plot_colors, plot_types, y_axes):
    if plot_colors is None:
        plot_colors = {}
    if plot_types is None:
        plot_types = {}
    for y in y_axes:
        chart_types = ["Line", "Scatter", "Bar"]
        index = chart_types.index(plot_types[y]) if y in plot_types else 0
        plot_types[y] = st.sidebar.radio(f"Select plot type for {y}", chart_types, index=index)
        if not enable_color_mode:
            plot_colors[y] = st.sidebar.color_picker(f"Select color for {y}", value=plot_colors.get(y, "#1f77b4"))
    return plot_colors, plot_types


def filter_sub_selection(df, filter_column, filter_range):
    filter_column = st.sidebar.selectbox("Select Column to Filter", df.select_dtypes(include=[np.number]).columns,
                                         index=df.select_dtypes(include=[np.number]).columns.get_loc(
                                             filter_column) if filter_column in df.columns else 0)
    min_val, max_val = df[filter_column].min(), df[filter_column].max()
    filter_range = st.sidebar.slider(
        "Select Range", min_value=int(min_val),
        max_value=min(int(max_val), MAX_STREAMLIT_SLIDER_VALUE),
        value=[int(filter_range[0]), int(filter_range[1])] if filter_range else (
            int(min_val), min(int(max_val), MAX_STREAMLIT_SLIDER_VALUE)),
        step=1
    )
    df = df[(df[filter_column] >= filter_range[0]) & (df[filter_column] <= filter_range[1])].reset_index(drop=True)
    return df


# Optimize tick values: Limit to 30 unique values max
def limit_tick_values(values, max_ticks=30):
    values = np.sort(values)
    if len(values) > max_ticks:
        indices = np.linspace(0, len(values) - 1, max_ticks, dtype=int)
        values = values[indices]
    return values
