import pandas as pd
import networkx as nx
import streamlit as st

# Update this path to where your file is located
file_path = "/Users/dr.bingbongwong/Downloads/FAF5.7.1/FAF5.7.1.csv" 
# 1. Load the data, but only pull the specific columns we actually need 
# This keeps memory usage low and speeds up execution
needed_cols = ['dms_orig', 'dms_dest', 'dms_mode', 'tons_2024', 'tmiles_2024']
df_raw = pd.read_csv(file_path, usecols=needed_cols)

city_lookup = {
    # Alabama Regions
    11: "Birmingham, AL",
    12: "Mobile, AL",
    19: "Rest of Alabama",
    
    # Major Connecting Southeast/Midwest Hubs
    131: "Atlanta, GA",
    471: "Memphis, TN",
    171: "Chicago, IL",
    481: "Houston, TX",
    482: "Dallas, TX",
    61: "Los Angeles, CA"
}
#df_interregional['Origin_Name']=df_interregional['dms_orig'].map(city_lookup)
#df_interregional['Dest_Name']= df_interregional['dms_dest'].map(city_lookup)
# 1. Get a list of the numeric keys we want to keep
valid_codes = list(city_lookup.keys())

# 2. Filter the raw data: Keep rows where BOTH origin and destination match our city list
df_filtered = df_raw[
    df_raw['dms_orig'].isin(valid_codes) & 
    df_raw['dms_dest'].isin(valid_codes)
].copy()

df_grouped = df_filtered.groupby(['dms_orig', 'dms_dest', 'dms_mode']).sum().reset_index()

# 1. Group the data first
df_grouped = df_filtered.groupby(['dms_orig', 'dms_dest', 'dms_mode']).sum().reset_index()

# 2. Calculate Distance with the 1000x FAF5 scale correction factor included!
df_grouped['Distance'] = df_grouped.apply(
    lambda row: (row['tmiles_2024'] / row['tons_2024']) * 1000 if row['tons_2024'] > 0 else 0, 
    axis=1
)

# 3. Create df_interregional by dropping intra-regional trips
df_interregional = df_grouped[df_grouped['dms_orig'] != df_grouped['dms_dest']].copy()

# 4. Map names and modes directly to df_interregional
df_interregional['Origin_Name'] = df_interregional['dms_orig'].map(city_lookup)
df_interregional['Dest_Name'] = df_interregional['dms_dest'].map(city_lookup)

mode_lookup = {1: 'Truck', 2: 'Rail', 5: 'Air'}
df_interregional['Mode_Name'] = df_interregional['dms_mode'].map(mode_lookup)

# 5. Drop any unmapped NaN strings safely
df_interregional = df_interregional.dropna(subset=['Origin_Name', 'Dest_Name', 'Mode_Name'])

# 6. Apply financial and carbon formulas to the clean dataset
df_interregional['Total_Cost'] = df_interregional.apply(
    lambda row: row['Distance'] * 3 if row['Mode_Name'] == 'Truck' 
                else (row['Distance'] * 20 * 0.05 if row['Mode_Name'] == 'Rail' 
                else row['Distance'] * 20 * 0.45), 
    axis=1
)
df_interregional['Total_CO2'] = df_interregional.apply(
    lambda row: row['Distance'] * 20 * 0.151 if row['Mode_Name'] == 'Truck' 
                else (row['Distance'] * 20 * 0.022 if row['Mode_Name'] == 'Rail' 
                else row['Distance'] * 20 * 1.527), 
    axis=1
)

# 7. Apply capacity attributes
df_interregional['Current_Volume'] = df_interregional['tons_2024']
df_interregional['Max_Capacity'] = df_interregional.apply(
    lambda row: row['tons_2024'] if row['tons_2024'] > 1000 
                else row['tons_2024'] * 2,
    axis=1
)
def optimize_real_freight_route(dataframe,origin,destination,weight_preference):
    G = nx.DiGraph()
    for _, row in dataframe.iterrows():
            if row['Current_Volume'] < row['Max_Capacity']:
                G.add_edge(
                row['Origin_Name'], 
                row['Dest_Name'], 
                mode=row['Mode_Name'],
                cost=row['Total_Cost'],
                co2=row['Total_CO2']
            )
            else: 
                print(f"Lane {row['Origin_Name']} -> {row['Dest_Name']} is at maximum capacity!")
    if not nx.has_path(G, origin, destination):
        return f"No path found between {origin} and {destination}"
        # Map friendly preference names to actual dataframe/graph attributes
    weight_attribute = 'cost' if weight_preference == 'Total_Cost' else 'co2'
    
        # Run Dijkstra's shortest path algorithm via NetworkX
    optimal_path = nx.shortest_path(G, source=origin, target=destination, weight=weight_attribute)
    
    return optimal_path


# 1. Extract a clean, unique list of all valid cities in your database
available_cities = sorted(list(set(df_interregional['Origin_Name'].unique()).union(set(df_interregional['Dest_Name'].unique()))))

st.sidebar.header("🕹️ Route Dispatch Parameters")

# 2. Generate interactive dropdown selectors
origin_select = st.sidebar.selectbox(
    "Select Shipping Origin:", 
    options=available_cities,
    index=available_cities.index("Birmingham, AL") # Default starting city
)

dest_select = st.sidebar.selectbox(
    "Select Shipping Destination:", 
    options=available_cities,
    index=available_cities.index("Mobile, AL") # Default ending city
)

# 3. Add the strategy selector radio buttons
metric_select = st.sidebar.radio(
    "Primary Network Objective:",
    options=["Total_Cost", "Total_CO2"],
    format_func=lambda x: "Minimize Freight Expenses ($)" if x == "Total_Cost" else "Minimize Carbon Footprint (CO2)"
)

# Create a prominent button in the sidebar to execute the model
if st.sidebar.button("🚚 Optimize & Dispatch Freight"):
    
    # 1. Prevent the user from routing a city to itself
    if origin_select == dest_select:
        st.error("❌ Error: Origin and Destination hubs must be different locations.")
        
    else:
        # 2. Run your real data function using the dropdown variables!
        route_result = optimize_real_freight_route(
            dataframe=df_interregional,
            origin=origin_select,
            destination=dest_select,
            weight_preference=metric_select
        )
        
        # 3. Handle a network bottleneck error (if the function returned a string)
        if isinstance(route_result, str):
            st.error(route_result)
            
        else:
            # 4. Success Layout: Display the path sequence nicely on the dashboard
            st.subheader("🎯 Recommended Dispatch Routing Strategy")
            
            # Format the output list into a clean visual path string
            visual_path = " ➡️ ".join(route_result)
            st.info(f"**Optimal Node Sequence:** {visual_path}")
            
            # 5. Bonus Data View: Filter the dataframe to show only the selected legs
            st.subheader("📊 Manifest Details for Selected Path Links")
            
            # Loop through the optimal path to pull row-by-row leg data for a table
            leg_rows = []
            for i in range(len(route_result) - 1):
                leg_match = df_interregional[
                    (df_interregional['Origin_Name'] == route_result[i]) & 
                    (df_interregional['Dest_Name'] == route_result[i+1])
                ]
                if not leg_match.empty:
                    # Pick the leg that matches our active optimization preference
                    best_leg_row = leg_match.sort_values(
                        by='Total_Cost' if metric_select == 'Total_Cost' else 'Total_CO2'
                    ).iloc[0]
                    leg_rows.append(best_leg_row)
            
            if leg_rows:
                df_path_summary = pd.DataFrame(leg_rows)
                
                # Show key business columns as a sleek dashboard table
                display_cols = ['Origin_Name', 'Dest_Name', 'Mode_Name', 'Distance', 'Total_Cost', 'Total_CO2']
                st.dataframe(df_path_summary[display_cols].reset_index(drop=True))
                
                # Sum and display totals
                total_cost_sum = df_path_summary['Total_Cost'].sum()
                total_co2_sum = df_path_summary['Total_CO2'].sum()
                
                col1, col2 = st.columns(2)
                col1.metric("Total Manifest Cost", f"${total_cost_sum:,.2f}")
                col2.metric("Total CO2 Footprint", f"{total_co2_sum:,.2f} kg")

