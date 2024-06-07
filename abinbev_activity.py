import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import json

def load_data(file_path):
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
    return data

# Define color mapping
def color_mapping(val):
    if pd.isna(val) or val == '':
        return 'background-color: white; color: black'
    elif val == 'Done early':
        return 'background-color: lightblue; color: black'
    elif val == 'Done on time':
        return 'background-color: lightgreen; color: black'
    elif val == 'Pending':
        return 'background-color: lightyellow; color: black'
    elif val == 'Not done on time':
        return 'background-color: lightcoral; color: black'
    elif val == 'Done by nature':
        return 'background-color: lightgrey; color: black'
    else:
        return 'background-color: white; color: black'

# Special handling for the "FarmName" column
def farmname_color_mapping(val):
    return 'background-color: white; color: black'

# Functions for farm information dashboard
def filter_farms(data):
    return data['farmName'].unique()

def display_farm_info(data, farm_name):
    farm_data = data[data['farmName'] == farm_name]

    for index, row in farm_data.iterrows():
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(row['Image URL'], caption=f"Image {index + 1}", use_column_width=True)
        
        with col2:
            st.write("Farm Name:", row['farmName'])
            st.write("Other Information:")
            
            json_data = json.loads(row['json data'])
            for item in json_data:
                st.write(f"{item['name']}: {item['value']}")

# Functions for macro and micro view
def generate_summary(data):
    #data['Plot Area in Bigha'] = data['Plot Area in m2'] * 0.00123
    total_plot_area_bigha = 82.28#data.groupby('FarmName')['Plot Area in Bigha'].first().sum()
    num_farms = 59  # Assuming 59 as a fixed value for the number of farms
    activities_summary = data['Activity'].value_counts()
    total_dap = data['DAP(kg)'].sum()
    total_mop = data['MOP(kg)'].sum()
    seed_varieties = data['Seed Variety'].dropna().unique()
    avg_germination_rate = data['GERMINATION VALUE(%)'].mean(skipna=True)
    max_germination_rate = data['GERMINATION VALUE(%)'].max()

    num_irrigation_done = data['Irrigation Done'].notna().sum()
    num_sprinkler_installed = data['Sprinker installed'].notna().sum() if 'Sprinker installed' in data.columns else 0
    total_seed_used = data['SEED'].sum()

    summary_data = {
        'Total Plot Area (Bigha)': total_plot_area_bigha,
        'Number of Farms': num_farms,
        'Total DAP (kg)': total_dap,
        'Total MOP (kg)': total_mop,
        'Total Seed Used (kg)': total_seed_used,
        'Maximum Germination Rate (%)': max_germination_rate,
        'Irrigation Done': num_irrigation_done,
        'Sprinkler Installed': num_sprinkler_installed
    }
    summary_df = pd.DataFrame(list(summary_data.items()), columns=['Metric', 'Value'])
    return summary_df, activities_summary, seed_varieties

def generate_fertilizer_usage(data):
    data['Plot Area in Bigha'] = data['Plot Area in m2'] * 0.00123
    data['DAP per Bigha'] = data['DAP(kg)'] / data['Plot Area in Bigha']
    data['MOP per Bigha'] = data['MOP(kg)'] / data['Plot Area in Bigha']
    fertilizer_usage = data.groupby('FarmName')[['DAP per Bigha', 'MOP per Bigha']].mean().reset_index()
    return fertilizer_usage

def generate_seed_usage(data):
    data['Plot Area in Bigha'] = data['Plot Area in m2'] * 0.00123
    data['Seed per Bigha'] = data['SEED'] / data['Plot Area in Bigha']
    seed_usage = data.groupby('FarmName')['Seed per Bigha'].mean().reset_index()
    return seed_usage

def generate_germination_by_farmer(data):
    germination_by_farmer = data.groupby('FarmName')['GERMINATION VALUE(%)'].max().reset_index()
    return germination_by_farmer

def generate_activity_over_time(data):
    activity_over_time = data.groupby(['Date', 'Activity']).size().reset_index(name='Counts')
    return activity_over_time

def generate_tillage_operations(data):
    tillage_operations = data['tillage'].value_counts()
    return tillage_operations

def generate_gantt_data(data):
    gantt_data = data[['Date', 'Activity', 'FarmName']].rename(columns={'Date': 'Start', 'Activity': 'Task', 'FarmName': 'Resource'})
    gantt_data['Finish'] = gantt_data['Start']  # Assuming activities are single-day events for now
    return gantt_data

# Streamlit app layout and functionality
st.set_page_config(layout="wide")
st.title('Dashboard')

data = None

# Sidebar selection for dashboards
dashboard_options = ['Macro View', 'Micro View', 'Farm Information', 'Activity Status']
selected_dashboard = st.sidebar.radio("Select Dashboard", dashboard_options)

# Macro View and Micro View functionalities
if selected_dashboard in ['Macro View', 'Micro View']:
    csv_path1 = "https://raw.githubusercontent.com/sakshamraj4/abinbev/main/data.csv"
    csv_path3 = "https://raw.githubusercontent.com/sakshamraj4/abinbev/main/activity_avinbev.csv"
    csv_path2 = "https://raw.githubusercontent.com/sakshamraj4/abinbev/main/data.csv"
    csv_path4 = "https://raw.githubusercontent.com/sakshamraj4/abinbev/main/test1.csv"

    if selected_dashboard == 'Macro View':
        data = load_data(csv_path1)
    elif selected_dashboard == 'Micro View':
        data = load_data(csv_path2)

if selected_dashboard == 'Macro View':
    if data is not None:
        st.sidebar.header('Filters')
        date_range = st.sidebar.date_input("Select Date Range", [])        
        varieties = []
        if 'Seed Variety' in data.columns:  # Check if 'Seed Variety' column exists
            varieties = st.sidebar.multiselect("Select Seed Varieties", options=data['Seed Variety'].dropna().unique())        
        if date_range and len(date_range) == 2:
            data = data[(data['Date'] >= pd.to_datetime(date_range[0])) & (data['Date'] <= pd.to_datetime(date_range[1]))]
        if varieties:
            data = data[data['Seed Variety'].isin(varieties)]
        
        st.header('Summarized View for Overall Farms')
        summary_df, activities_summary, seed_varieties = generate_summary(data)
        st.dataframe(summary_df)

        st.write('### Fertilizer Usage (KG/Bigha) by Farm')
        fertilizer_usage = generate_fertilizer_usage(data)
        fig_fertilizer = px.bar(fertilizer_usage, x='FarmName', y=['DAP per Bigha', 'MOP per Bigha'], barmode='group', title='Fertilizer Usage (KG/Bigha) by Farm')
        st.plotly_chart(fig_fertilizer)

        st.write('### Seed Usage (KG/Bigha) by Farm')
        seed_usage = generate_seed_usage(data)
        fig_seed_usage = px.bar(seed_usage, x='FarmName', y='Seed per Bigha', title='Seed Usage (KG/Bigha) by Farm')
        st.plotly_chart(fig_seed_usage)

        st.write('### Germination Percentage(latest) by Farmer')
        germination_by_farmer = generate_germination_by_farmer(data)
        st.dataframe(germination_by_farmer)

        st.write('### Activities Summary')
        st.bar_chart(activities_summary)
        st.write('### Activity Occurrences Over Time')
        activity_over_time = generate_activity_over_time(data)
        fig = px.line(activity_over_time, x='Date', y='Counts', color='Activity', title='Activity Occurrences Over Time')
        st.plotly_chart(fig)
        st.write('### Seed Varieties Used')
        st.write(seed_varieties)

        st.write('### Tillage Operations')
        tillage_operations = generate_tillage_operations(data)
        st.bar_chart(tillage_operations)
    else:
        st.write("Please upload a CSV file for the Macro View dashboard.")

            

elif selected_dashboard == 'Micro View':
    st.sidebar.header('Filters')
    farmer_selected = st.sidebar.selectbox("Select Farmer", options=data['FarmName'].unique())
    date_range = st.sidebar.date_input("Select Date Range", [])

    if farmer_selected:
        data = data[data['FarmName'] == farmer_selected]
    if date_range and len(date_range) == 2:
        data = data[(data['Date'] >= pd.to_datetime(date_range[0])) & (data['Date'] <= pd.to_datetime(date_range[1]))]

    st.write('### Activity Details')
    st.dataframe(data)

    st.write('### Detailed Metrics')

    st.write('### Germination Movement Over Time')
    germination_over_time = data[['Date', 'GERMINATION VALUE(%)']].sort_values(by='Date')
    st.line_chart(germination_over_time.set_index('Date'))

    st.write('#### Fertilizer Usage')
    st.dataframe(data[['Date', 'DAP(kg)', 'MOP(kg)']])

    st.write('#### Seed Usage')
    st.dataframe(data[['Date', 'SEED', 'Seed Variety']])

    st.write('#### Germination Values')
    st.dataframe(data[['Date', 'GERMINATION VALUE(%)']])

    st.write('#### Irrigation Status')
    st.dataframe(data[['Date', 'Irrigation Done', 'Channels Constructed', 'Sprinker installed']] if 'Sprinker installed' in data.columns else data[['Date', 'Irrigation Done', 'Channels Constructed']])
    
    st.write('#### Tillage Operations')
    st.dataframe(data[['Date', 'tillage']])

    st.write('### Gantt Chart of Activities')
    gantt_data = generate_gantt_data(data)
    fig_gantt = ff.create_gantt(gantt_data, index_col='Resource', show_colorbar=True, group_tasks=True, title='Gantt Chart of Activities', showgrid_x=True, showgrid_y=True)
    st.plotly_chart(fig_gantt)        

# Farm Information Dashboard
elif selected_dashboard == 'Farm Information':
    st.title("Farm Information Dashboard") 
    uploaded_file = "https://raw.githubusercontent.com/sakshamraj4/abinbev/main/test1.csv"

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)

        if 'json data' not in data.columns:
            st.error("The 'json data' column is not present in the uploaded file.")
        else:
            farms = filter_farms(data)
            selected_farm = st.selectbox("Select Farm", farms)

            if selected_farm:
                display_farm_info(data, selected_farm)

# Activity Status Dashboard
elif selected_dashboard == 'Activity Status':
    st.title("Activity Status Dashboard")
    uploaded_file_activity = "https://raw.githubusercontent.com/sakshamraj4/abinbev/main/activity_avinbev.csv"

    if uploaded_file_activity is not None:
        # Read the CSV file
        df_activity = pd.read_csv(uploaded_file_activity)
        
        # Replace NaN values with an empty string
        df_activity = df_activity.fillna('')
        
        # Apply the color mapping
        styled_df = df_activity.style.applymap(color_mapping)
        
        # Apply special styling for "FarmName" column
        if 'FarmName' in df_activity.columns:
            styled_df = styled_df.applymap(farmname_color_mapping, subset=['FarmName'])
        
        styled_df = styled_df.set_table_styles(
            [{
                'selector': 'th',
                'props': [('background-color', '#333'), ('color', 'white')]
            }, {
                'selector': 'td',
                'props': [('border', '1px solid #ddd'), ('padding', '8px')]
            }]
        ).set_properties(
            **{
                'font-size': '15px',
                'font-family': 'Arial',
                'border': '1px solid #ddd'
            }
        )

        # Display the styled dataframe
        st.write(styled_df.to_html(), unsafe_allow_html=True)
    else:
        st.write("Please upload a CSV file for the Activity Status dashboard.")

# Run the app
