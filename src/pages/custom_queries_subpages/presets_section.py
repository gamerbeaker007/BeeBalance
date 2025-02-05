import streamlit as st

graph_presets = {
    'HP vs KE Ratio': {
        'x_axis': 'hp',
        'y_axes': ['hp', 'ke_ratio', 'posting_rewards'],
        'y_log': True,
        'plot_types': {
            'hp': 'Line',
            'ke_ratio': 'Scatter',
            'posting_rewards': 'Scatter',
        },
        'plot_colors': {
            'hp': '#FF0000',
            'ke_ratio': '#FFFF00',
            'posting_rewards': '#0000FF',
        },
        'sort_column': 'hp',
        'sort_order': 'Descending',
        'enable_filter': False,
    },
    # 'Test 1': {
    #     'x_axis': 'name',
    #     'y_axes': ['hive', 'hp'],
    #     'plot_types': {
    #         'hive': 'Bar',
    #         'hp': 'Scatter',
    #     },
    #     'plot_colors': {'hp': '#FF0000'},
    #     'sort_column': 'hp',
    #     'sort_order': 'Descending',
    #     'enable_filter': True,
    #     'enable_bubble_size': True,
    #     'bubble_column': 'hbd',
    #     'filter_column': 'hbd',
    #     'enable_ref_line': True,
    #     'ref_value': 50000,
    #     'ref_color': '#FF0000',
    #     'filter_range': (10, 25000),
    # },
    'SPSP': {
        'x_axis': 'name',
        'y_axes': ['spsp'],
        'sort_column': 'spsp',
        'sort_order': 'Descending',
    },
}


def get_preset_section(df):
    """Dynamically generate preset buttons based on available columns in df."""

    # Ensure session state exists for selected preset
    if 'selected_preset' not in st.session_state:
        st.session_state.selected_preset = None

    valid_presets = {}  # Dictionary to store only valid presets

    # Filter presets based on the presence of required columns
    for preset_name, preset_params in graph_presets.items():
        x_axis = preset_params.get('x_axis')
        y_axes = preset_params.get('y_axes', [])
        required_columns = [x_axis] + y_axes  # List of all required columns

        # Check if all required columns exist in df
        if all(col in df.columns for col in required_columns):
            valid_presets[preset_name] = preset_params

    # Generate buttons dynamically

    # Create dynamic button layout (distributes buttons evenly)
    preset_names = list(valid_presets.keys())
    num_buttons = len(preset_names)
    if num_buttons > 0:
        st.subheader('📊 Available Presets')
        cols = st.columns(min(num_buttons, 5))

        for i, preset_name in enumerate(preset_names):
            with cols[i % 5]:  # Distribute buttons across columns
                if st.button(preset_name):
                    st.session_state.selected_preset = preset_name

    # Return selected preset parameters
    selected_preset = st.session_state.selected_preset
    return valid_presets.get(selected_preset, {})
