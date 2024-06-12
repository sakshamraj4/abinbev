import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import json
import datetime


# Password check function
def check_password():
    def password_entered():
        if st.session_state["password"] == "Abinbev@123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store the password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True


# App code
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)
    return data


# Custom color mapping function for Growth Tracker
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

def conditional_color_mapping(val, col):
    if col == 'Seeding Rate':
        if 7.5 <= val <= 8.5:
            color = 'lightgreen'
        else:
            color = 'red'
    elif col == 'DAP/MOP Fertilizer Applied quantity':
        if 9.5 <= val <= 10.5:
            color = 'lightgreen'
        else:
            color = 'red'
    elif col == 'UREA1 Fertilizer Applied quantity':
        if 6.5 <= val <= 7.5:
            color = 'lightgreen'
        else:
            color = 'red'
    else:
        color = ''
    return f'background-color: {color}'



# Custom color mapping function for Growth Tracker dashboard
def growth_tracker_color_mapping(val):
    if val == 'current':
        return 'background-color: yellow; color: black'
    elif val == 'well and passed':
        return 'background-color: green; color: black'
    elif val == '':
        return 'background-color: white; color: black'
    elif val == 'not followed':
        return 'background-color: red; color: black'
    else:
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

            st.write("#### Activity ")
            st.write(row['activity_record'])


# Functions for macro and micro view
import datetime
import pandas as pd

import pandas as pd
from datetime import datetime, timedelta


def generate_summary(data):
    # Convert 'Date' column to datetime type
    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True, errors='coerce')
    # Calculate today's date
    today = datetime.now().strftime('%d/%m/%Y')
    # Filter the DataFrame for today's date
    today_data = data[data['Date'].dt.strftime('%d/%m/%Y') == today]
    # Calculate yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    yesterday = yesterday.strftime('%d/%m/%Y')
    # Filter the DataFrame for yesterday's date
    yesterday_data = data[data['Date'].dt.strftime('%d/%m/%Y') == yesterday]
    # Calculate two days ago
    two_days_ago = datetime.now() - timedelta(days=2)
    two_days_ago = two_days_ago.strftime('%d/%m/%Y')
    # Filter the DataFrame for two days ago
    two_days_ago_data = data[data['Date'].dt.strftime('%d/%m/%Y') == two_days_ago]
    # Count unique entries in 'FarmName' column for each day
    total_visited_today = today_data['FarmName'].nunique()
    total_visited_yesterday = yesterday_data['FarmName'].nunique()
    total_visited_two_days_ago = two_days_ago_data['FarmName'].nunique()
    # Other summary calculations
    total_plot_area_bigha = 82.28  # Fixed value for the number of farms
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
    # Create summary data dictionary
    summary_data = {
        'Total Plot Area (Bigha)': total_plot_area_bigha,
        'Number of Farms': num_farms,
        'Total DAP (kg)': total_dap,
        'Total MOP (kg)': total_mop,
        'Total Seed Used (kg)': total_seed_used,
        'Maximum Germination Rate (%)': max_germination_rate,
        'Irrigation Done': num_irrigation_done,
        'Sprinkler Installed': num_sprinkler_installed,
        'Total Plot Visited Today': total_visited_today,
        'Total Plot Visited Yesterday': total_visited_yesterday,
        'Total Plot Visited Two Days Ago': total_visited_two_days_ago,
        'Activity Details Last Date': activities_summary
    }
    # Create summary DataFrame
    summary_df = pd.DataFrame(list(summary_data.items()), columns=['Metric', 'Value'])
    # Return summary DataFrame along with other calculated values
    return summary_df, activities_summary, seed_varieties

def generate_fertilizer_usage(data):
    fertilizer_usage = data[['Farm Name', 'DAP/MOP Fertilizer Applied quantity', 'UREA1 Fertilizer Applied quantity']]
    return fertilizer_usage

# Function to generate seed usage summary
def generate_seed_usage(data):
    seed_usage = data[['Farm Name', 'Seeding Rate']]
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
    gantt_data = data[['Date', 'Activity', 'FarmName']].rename(
        columns={'Date': 'Start', 'Activity': 'Task', 'FarmName': 'Resource'})
    gantt_data['Finish'] = gantt_data['Start']  # Assuming activities are single-day events for now
    return gantt_data


# Streamlit app layout and functionality
if check_password():
    st.set_page_config(layout="wide")
    st.title('Dashboard')

    data = None

    # Sidebar selection for dashboards
    dashboard_options = ['Activity Status', 'Growth Tracker', 'Operations Tracker', 'Farm Information', 'Macro View',
                         'Micro View']
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
            uploaded_file_operations = "https://raw.githubusercontent.com/sakshamraj4/abinbev/main/operations.csv"
            data1 = pd.read_csv(uploaded_file_operations)
            varieties = []
            if 'Seed Variety' in data.columns:  # Check if 'Seed Variety' column exists
                varieties = st.sidebar.multiselect("Select Seed Varieties",
                                                   options=data['Seed Variety'].dropna().unique())
            if date_range and len(date_range) == 2:
                data = data[
                    (data['Date'] >= pd.to_datetime(date_range[0])) & (data['Date'] <= pd.to_datetime(date_range[1]))]
            if varieties:
                data = data[data['Seed Variety'].isin(varieties)]

            st.header('Summarized View for Overall Farms')
            summary_df, activities_summary, seed_varieties = generate_summary(data)
            st.write(summary_df)

            st.write('### DAP/MOP Fertilizer Applied Quantity (KG/Bigha) by Farm')
            fertilizer_usage = generate_fertilizer_usage(data1)
            fig_dap_mop = px.bar(fertilizer_usage, x='Farm Name', y='DAP/MOP Fertilizer Applied quantity',
                                 title='DAP/MOP Fertilizer Applied Quantity (KG/Bigha) by Farm')
            fig_dap_mop.add_shape(
                type='line',
                x0=-0.5, x1=len(fertilizer_usage['Farm Name']) - 0.5,
                y0=10, y1=10,
                line=dict(color='white', dash='dash')
            )
            st.plotly_chart(fig_dap_mop)

            st.write('### UREA1 Fertilizer Applied Quantity (KG/Bigha) by Farm')
            fig_urea1 = px.bar(fertilizer_usage, x='Farm Name', y='UREA1 Fertilizer Applied quantity',
                               title='UREA1 Fertilizer Applied Quantity (KG/Bigha) by Farm')
            fig_urea1.add_shape(
                type='line',
                x0=-0.5, x1=len(fertilizer_usage['Farm Name']) - 0.5,
                y0=7, y1=7,
                line=dict(color='white', dash='dash')
            )
            st.plotly_chart(fig_urea1)

            st.write('### Seed Usage (KG/Bigha) by Farm')
            seed_usage = generate_seed_usage(data1)
            fig_seed_usage = px.bar(seed_usage, x='Farm Name', y='Seeding Rate',
                                    title='Seed Usage (KG/Bigha) by Farm')
            fig_seed_usage.add_shape(
                type='line',
                x0=-0.5, x1=len(seed_usage['Farm Name']) - 0.5,
                y0=8, y1=8,
                line=dict(color='white', dash='dash')
            )
            st.plotly_chart(fig_seed_usage)

            st.write('### Germination Percentage(latest) by Farmer')
            germination_by_farmer = generate_germination_by_farmer(data)
            st.dataframe(germination_by_farmer)

            st.write('### Activities Summary')
            st.bar_chart(activities_summary)
            st.write('### Activity Occurrences Over Time')
            activity_over_time = generate_activity_over_time(data)
            fig = px.line(activity_over_time, x='Date', y='Counts', color='Activity',
                          title='Activity Occurrences Over Time')
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
            data = data[
                (data['Date'] >= pd.to_datetime(date_range[0])) & (data['Date'] <= pd.to_datetime(date_range[1]))]
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
        st.dataframe(data[['Date', 'Irrigation Done', 'Channels Constructed',
                           'Sprinker installed']] if 'Sprinker installed' in data.columns else data[
            ['Date', 'Irrigation Done', 'Channels Constructed']])
        st.write('#### Tillage Operations')
        st.dataframe(data[['Date', 'tillage']])
        st.write('### Gantt Chart of Activities')
        gantt_data = generate_gantt_data(data)
        fig_gantt = ff.create_gantt(gantt_data, index_col='Resource', show_colorbar=True, group_tasks=True,
                                    title='Gantt Chart of Activities', showgrid_x=True, showgrid_y=True)
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
            st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)
            st.markdown("""<style>
                th:first-child {position: sticky; left: 0; background-color: #f1f1f1;}
                td:first-child {position: sticky; left: 0; background-color: #f1f1f1;}
                tr:first-child th {position: sticky; top: 0; background-color: #f1f1f1;}
                </style>""", unsafe_allow_html=True)
        else:
            st.write("Please upload a CSV file for the Activity Status dashboard.")

    # Growth Tracker Dashboard
    elif selected_dashboard == 'Growth Tracker':
        st.title("Growth Tracker Dashboard")
        uploaded_file_growth = "https://raw.githubusercontent.com/sakshamraj4/abinbev/main/Growth_Tracker.csv"
        if uploaded_file_growth is not None:
            # Read the CSV file
            df_growth = pd.read_csv(uploaded_file_growth)
            # Replace NaN values with an empty string
            df_growth = df_growth.fillna('')
            # Apply the growth tracker color mapping
            styled_df_growth = df_growth.style.applymap(lambda val: growth_tracker_color_mapping(val))
            for column in df_growth.columns:
                if column == 'Farm Name':
                    styled_df_growth.set_properties(**{'color': 'grey'}, subset=pd.IndexSlice[:, column])
            # Set custom table styles
            styled_df_growth = styled_df_growth.set_table_styles(
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
            st.write(styled_df_growth.to_html(), unsafe_allow_html=True)
            st.markdown("""<style>
                th:first-child {position: sticky; left: 0; background-color: #f1f1f1;}
                td:first-child {position: sticky; left: 0; background-color: #f1f1f1;}
                tr:first-child th {position: sticky; top: 0; background-color: #f1f1f1;}
                </style>""", unsafe_allow_html=True)
        else:
            st.write("Please upload a CSV file for the Growth Tracker dashboard.")




    elif selected_dashboard == 'Operations Tracker':
        st.title("Operations Tracker Dashboard")

        uploaded_file_operations = "https://raw.githubusercontent.com/sakshamraj4/abinbev/main/operations.csv"

        if uploaded_file_operations is not None:
        # Read the CSV file
            df_operations = pd.read_csv(uploaded_file_operations)

        # Replace NaN values with an empty string or any other suitable method
            df_operations = df_operations.fillna('')
            df_operations = df_operations.astype(str)

        # Convert specific columns to numeric type
            decimal_columns = ['Seeding Rate', 'DAP/MOP Fertilizer Applied quantity', 'UREA1 Fertilizer Applied quantity']
            df_operations[decimal_columns] = df_operations[decimal_columns].apply(pd.to_numeric, errors='coerce')

        # Round the specified columns to 2 decimal places
            df_operations[decimal_columns] = df_operations[decimal_columns].round(2)

        # Apply the conditional color mapping
            styled_df_operations = df_operations.style.apply(lambda x: [conditional_color_mapping(v, x.name) for v in x], subset=decimal_columns)

        # Apply special styling for specific columns if needed
            if 'Column_Name' in df_operations.columns:
                styled_df_operations = styled_df_operations.applymap(custom_color_mapping, subset=['Column_Name'])

        # Set custom table styles
            styled_df_operations = styled_df_operations.set_table_styles(
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
            st.write(styled_df_operations.to_html(), unsafe_allow_html=True)
            st.markdown("""<style>
                th:first-child {position: sticky; left: 0; background-color: #f1f1f1;}
                td:first-child {position: sticky; left: 0; background-color: #f1f1f1;}
                tr:first-child th {position: sticky; top: 0; background-color: #f1f1f1;}
                </style>""", unsafe_allow_html=True)

        else:
            st.write("Please upload a CSV file for the Operations Tracker dashboard.")
