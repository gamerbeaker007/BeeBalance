import numpy as np
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
    st.title("Customizable Graph in Streamlit")

    # Sidebar options
    st.sidebar.header("Graph Settings")

    # X-axis selection (single select) with preset default
    x_axis = st.sidebar.selectbox("Select X-axis", df.columns, index=df.columns.get_loc(x_axis) if x_axis in df.columns else 0)

    # Y-axis selection (multiple select) with preset default
    if y_axes:
        default = [y for y in y_axes if y in df.columns]
    else:
        default = [df.columns[1]]
    y_axes = st.sidebar.multiselect("Select Y-axis", df.columns, default=default)

    # Check if any selected Y-axis column is categorical
    is_y_categorical = any(df[y].dtype == "O" for y in y_axes)

    # X-axis log scale (disabled if categorical)
    x_log = st.sidebar.checkbox("Log Scale for X-axis", disabled=(df[x_axis].dtype == "O"), value=x_log)

    # Y-axis log scale (disabled if any selected Y-axis is categorical)
    y_log = st.sidebar.checkbox("Log Scale for Y-axis", disabled=is_y_categorical,
                                value=y_log if is_y_categorical else y_log)

    # Sorting options with preset defaults
    st.sidebar.subheader("Sorting Options")
    sort_column = st.sidebar.selectbox("Select Column to Sort", df.columns, index=df.columns.get_loc(sort_column) if sort_column in df.columns else 0)
    sort_order = st.sidebar.radio("Sort Order", ["Ascending", "Descending"], index=0 if sort_order == "Ascending" else 1)

    # Apply Sorting and Reset Index
    df = df.sort_values(by=sort_column, ascending=(sort_order == "Ascending")).reset_index(drop=True)

    # Filtering options
    st.sidebar.subheader("Filtering Options")
    enable_filter = st.sidebar.checkbox("Enable Filtering", value=enable_filter)

    if enable_filter:
        # Select column for filtering (only numerical columns)
        filter_column = st.sidebar.selectbox("Select Column to Filter", df.select_dtypes(include=[np.number]).columns,
                                             index=df.select_dtypes(include=[np.number]).columns.get_loc(filter_column) if filter_column in df.columns else 0)

        # Get min and max values of the selected column
        min_val, max_val = df[filter_column].min(), df[filter_column].max()

        filter_range = st.sidebar.slider(
            "Select Range",
            min_value=int(min_val),
            max_value=min(int(max_val), MAX_STREAMLIT_SLIDER_VALUE),  # Ensure it does not exceed the limit
            value=[int(filter_range[0]), int(filter_range[1])] if filter_range else (
                int(min_val), min(int(max_val), MAX_STREAMLIT_SLIDER_VALUE)  # Cap default value too
            ),
            step=1
        )

        # Apply filter
        df = df[(df[filter_column] >= filter_range[0]) & (df[filter_column] <= filter_range[1])].reset_index(drop=True)

        # Check if the DataFrame is empty after filtering
        if df.empty:
            st.warning("⚠️ The selected filter range resulted in no data. Please adjust the filter criteria.")
            return  # Exit the function early to prevent rendering an empty chart

    # Select plot type and color for each Y-axis
    if plot_colors is None:
        plot_colors = {}
    if plot_types is None:
        plot_types = {}

    for y in y_axes:
        chart_types = ["Line", "Scatter", "Bar"]
        if y in plot_types:
            plot_type = plot_types[y]
            index = [i for i, val in enumerate(chart_types) if val == plot_type][0]
        else:
            index=0
        plot_types[y] = st.sidebar.radio(f"Select plot type for {y}", chart_types, index=index)

        if y in plot_colors:
            default_color = plot_colors[y]
        else:
            default_color = "#1f77b4"
        plot_colors[y] = st.sidebar.color_picker(f"Select color for {y}", value=default_color)

    # Bubble size settings (for scatter plots)
    enable_bubble_size = st.sidebar.checkbox("Enable Bubble Size", True if enable_bubble_size else None)
    log_scale_factor = 5.0  # Default log scale factor

    if enable_bubble_size:
        # Filter numeric columns for bubble size selection
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if bubble_column in numeric_columns:
            index = [i for i, val in enumerate(numeric_columns) if val == bubble_column][0]
        else:
            index = 0
        bubble_column = st.sidebar.selectbox("Select Bubble Size Column", numeric_columns, index=index)

        # Slider to adjust log scale granularity
        log_scale_factor = st.sidebar.slider("Bubble Size Log Scale Factor", 1.0, 10.0, 5.0, step=0.1)

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

    # Optimize tick values: Limit to 30 unique values max
    def limit_tick_values(values, max_ticks=30):
        values = np.sort(values)
        if len(values) > max_ticks:
            indices = np.linspace(0, len(values) - 1, max_ticks, dtype=int)
            values = values[indices]
        return values

    # Get optimized tick values for log scale
    x_ticks = limit_tick_values(df[x_axis].unique()) if x_log and df[x_axis].dtype != "O" else None
    y_ticks = limit_tick_values(np.unique(df[y_axes].values)) if y_log else None

    # Enable Reference Line
    enable_ref_line = st.sidebar.checkbox("Enable Reference Line", True if enable_ref_line else None)
    ref_value = st.sidebar.number_input("Reference Line Value", ref_value if ref_value else 0) if enable_ref_line else None
    ref_color = st.sidebar.color_picker("Reference Line Color", ref_color if ref_color else "#FF0000") if enable_ref_line else None

    # Convert X-axis to string if categorical
    if df[x_axis].dtype == "O":
        df[x_axis] = df[x_axis].astype(str)

    # Apply log scale to bubble sizes (if selected)
    if enable_bubble_size and bubble_column:
        # Define a minimum bubble size threshold
        min_bubble_size = 5  # Adjust as needed

        # Apply log scale to bubble sizes and ensure a minimum size
        df["bubble_size"] = np.clip(np.log1p(df[bubble_column]) * log_scale_factor, min_bubble_size, None)
    else:
        df["bubble_size"] = 10  # Default fixed size if bubble size is not enabled

    # Plot
    fig = go.Figure()

    for y in y_axes:
        if plot_types[y] == "Line":
            fig.add_trace(go.Scatter(
                x=df[x_axis],
                y=df[y],
                mode="lines",
                name=y,
                line=dict(color=plot_colors[y]),
                hovertext=df["hover_text"] if enable_hover else None,
                hoverinfo="text" if enable_hover else "none"
            ))
        elif plot_types[y] == "Scatter":
            fig.add_trace(go.Scatter(
                x=df[x_axis],
                y=df[y],
                mode="markers",
                name=y,
                marker=dict(
                    size=df["bubble_size"],
                    color=plot_colors[y],
                    line = dict(
                        color='white',  # Border color
                        width=1  # Border width
                    ),
                ),
                hovertext=df["hover_text"] if enable_hover else None,
                hoverinfo="text" if enable_hover else "none"
            ))
        elif plot_types[y] == "Bar":
            fig.add_trace(go.Bar(
                x=df[x_axis],
                y=df[y],
                name=y,
                marker=dict(color=plot_colors[y]),
                text=df["hover_text"] if enable_hover else None,
                hoverinfo="text" if enable_hover else "none"
            ))

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

    # Apply log scale if selected, ensuring categorical X-axis is handled properly
    fig.update_layout(
        xaxis=dict(
            type="log" if x_log and df[x_axis].dtype != "O" else "category",
            categoryorder="array",
            categoryarray=df[x_axis] if df[x_axis].dtype == "O" else None,
            tickvals=x_ticks if x_log else None,  # Use real values for tick marks
            tickmode="array" if x_log else None,
            showgrid=True,
            # zeroline=True,  # Always draw X=0 line
            # zerolinecolor="red",  # Make it visible
            # zerolinewidth=10
        ),
        yaxis=dict(
            type="log" if y_log else "linear",
            tickvals=y_ticks if y_log else None,  # Use real values for tick marks
            tickmode="array" if y_log else None,
            # zeroline=True,  # Always draw Y=0 line
            # zerolinecolor="yellow",  # Make it visible
            # zerolinewidth=1
        ),
        xaxis_title=x_axis,
        yaxis_title=','.join(y_axes),
        title=f"Customized Graph X: {x_axis} vs Y: {', '.join(y_axes)}",
        height=800  # Fixed height
    )

    # Add Reference Line if enabled
    if enable_ref_line:
        fig.add_hline(y=ref_value, line_dash="dash", line_color=ref_color, annotation_text=f"Ref: {ref_value}")

    st.plotly_chart(fig)
