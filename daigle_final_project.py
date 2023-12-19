"""
Class: CS230--Section 001
Name: Ashley Daigle
Description: (Give a brief description for Exercise name--See
below)
I pledge that I have completed the programming assignment
independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import pydeck as pdk

st.set_option('deprecation.showPyplotGlobalUse', False)


def map_day_to_full_name(day):  # function to turn abbreviated day from data into full name
    day_mapping = {
        'M': 'Monday',
        'T': 'Tuesday',
        'W': 'Wednesday',
        'TH': 'Thursday',
        'F': 'Friday',
        'MF': 'Monday & Friday',
        'MTH': 'Monday & Thursday',
        'TF': 'Tuesday & Friday',
    }
    return day_mapping.get(day, day)


def plot_day_by_coordinates(df):
    st.subheader('Boston Trash Collection Map')

    # colors for each day of the week
    dot_color = {
        'M': [0, 0, 255, 255],  # Blue
        'T': [0, 255, 0, 255],  # Green
        'W': [255, 165, 0, 255],  # Orange
        'TH': [255, 0, 0, 255],  # Red
        'F': [128, 0, 128, 255],  # Purple
        'MF': [0, 255, 255, 255],  # Cyan
        'MTH': [255, 182, 193, 255],  # Pink
        'TF': [165, 42, 42, 255],  # Brown
    }

    df['color'] = df['trashday'].map(dot_color)
    # criteria for the map
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["x_coord", "y_coord"],
        get_radius=2,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )
    # setting lat and lon to be the coordinates from the data set
    view_state = pdk.ViewState(
        latitude=df['y_coord'].mean(),
        longitude=df['x_coord'].mean(),
        zoom=11,
        pitch=0
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v9"
    )
    # legend that correlates dot color to trash pickup day
    legend_html = """
            <div style="position: fixed; top: 20px; right: 20px; z-index: 1000; padding: 10px; background-color: white; border: 1px solid grey; border-radius: 5px; font-size: 14px">
                <h4>Trash Day Legend</h4>
                <p><span style="color: blue;">Monday (M)</span></p>
                <p><span style="color: green;">Tuesday (T)</span></p>
                <p><span style="color: orange;">Wednesday (W)</span></p>
                <p><span style="color: red;">Thursday (TH)</span></p>
                <p><span style="color: purple;">Friday (F)</span></p>
                <p><span style="color: cyan;">Monday & Friday (MF)</span></p>
                <p><span style="color: pink;">Monday & Thursday (MTH)</span></p>
                <p><span style="color: brown;">Tuesday & Friday (TF)</span></p>
            </div>
        """

    st.pydeck_chart(deck)

    st.markdown(legend_html, unsafe_allow_html=True)


def customer_pickup_day(df):
    st.subheader('Find out your specified Trash Pickup Day(s)')
    address = st.text_input('Enter your address (No unit #): ')  # user inputs address
    towns = df['mailing_neighborhood'].unique()  # defining each town in the data set
    selected_town = st.selectbox('Select Town', towns)  # user selects town
    selected_zip = st.number_input('Enter Zip Code:', min_value=1000, max_value=9999,
                                   step=1)  # user enters 4 digit zip code

    # set case to false so user can enter lower or upper case, and find matches for user input in the data frame
    filtered_data = df[
        (df['full_address'].str.contains(address, case=False)) &
        (df['mailing_neighborhood'] == selected_town) &
        (df['zip_code'] == selected_zip)
        ]

    # Check if the filtered data is not empty
    if not filtered_data.empty:
        pickup_day_abrev = filtered_data['trashday'].values[0]
        pickup_day_full = map_day_to_full_name(pickup_day_abrev)  # to display full day of week instead of abbreviation
        st.success(
            f"Address found! Your trash pickup day is: {pickup_day_full}")  # if address matches, tells the user their trash pickup day
    else:
        st.warning("Sorry! We couldn't find that address.")  # warning displayed if the address is not in the dataset


def display_trashday_piechart(df):  # function to display a pie chart that shows % of days for trash pickup
    st.subheader("Distribution of Trash Pickup Days")
    day_counts = df.groupby('trashday').size().reset_index(name='count')

    # display full day names instead of just M, T, etc.
    day_counts['trashday_full'] = day_counts['trashday'].map(map_day_to_full_name)

    plt.figure(figsize=(10, 10))
    plt.pie(day_counts['count'], labels=day_counts['trashday_full'], autopct='%1.1f%%', startangle=90)
    plt.title('Trash Pickup Distribution by Day')
    st.pyplot()


def trash_day_by_mailing_neighborhood(df):
    st.subheader('Pickup Frequency by Day and Neighborhood')

    # Dropdown menu for selecting town
    neighborhoods = df['mailing_neighborhood'].unique()
    selected_neighborhood = st.selectbox('Select Neighborhood:', neighborhoods)

    # Filter the DataFrame based on the selected neighborhood
    filtered_df = df[df['mailing_neighborhood'] == selected_neighborhood]

    day_order = ['M', 'T', 'W', 'TH', 'F', 'MTH', 'MF', 'TF']

    filtered_df['trashday'] = pd.Categorical(filtered_df['trashday'], categories=day_order, ordered=True)

    # Group by trashday and calculate the pickup count
    pickup_count = filtered_df.groupby('trashday').size().reset_index(name='pickupcount')

    # Plot the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(pickup_count['trashday'], pickup_count['pickupcount'], color='pink')
    plt.title(f'Pickup Frequency by Day in {selected_neighborhood}')
    plt.xlabel('Trash Day')
    plt.ylabel('Pickup Count')
    st.pyplot()


def stacked_bar_by_neighborhood_and_day(df):
    st.subheader("Stacked bar chart of all neighborhoods and pickup days")

    # Calculate total pickups for each neighborhood
    pickup_count = df.groupby(['trashday', 'mailing_neighborhood']).size().reset_index(name='pickupcount')

    # Count the number of occurrences for each neighborhood
    neighborhood_counts = pickup_count.groupby('mailing_neighborhood').size().reset_index(name='count')

    # Sort neighborhoods by the count in ascending order
    sorted_neighborhoods = neighborhood_counts.sort_values(by='count', ascending=True)['mailing_neighborhood']

    # Filter the original pickup_count DataFrame based on the sorted neighborhoods
    pickup_count_sorted = pickup_count[pickup_count['mailing_neighborhood'].isin(sorted_neighborhoods)]

    day_order = ['M', 'T', 'W', 'TH', 'F', 'MTH', 'MF', 'TF']
    pickup_count_sorted['trashday'] = pd.Categorical(pickup_count_sorted['trashday'], categories=day_order,
                                                     ordered=True)
    pivot_df = pickup_count_sorted.pivot(index='mailing_neighborhood', columns='trashday', values='pickupcount')

    # Sort the DataFrame by total pickups for each neighborhood
    pivot_df['Total'] = pivot_df.sum(axis=1)
    pivot_df = pivot_df.sort_values(by='Total', ascending=True).drop(columns='Total')

    # Plot data as a stacked bar chart
    pivot_df.plot(kind='bar', stacked=True, figsize=(10, 10))

    # Define title and labels and legend for the graph
    plt.title('Pickup Frequency by Day and Neighborhood')
    plt.xlabel('Neighborhood')
    plt.ylabel('Pickup Count')
    plt.legend(title='Trash Day', bbox_to_anchor=(1.05, 1), loc='upper right')

    st.pyplot()


def see_addresses_by_zip_and_day(df):
    st.subheader(f'View Addresses by Pickup Day and Zip Code')
    unique_days = df['trashday'].unique()
    selected_day = st.selectbox('Select Day of Week:', unique_days)  # user selects day of the week
    selected_zip = st.number_input('Enter Zip Code:', min_value=1000, max_value=9999, step=1)  # user enters zip code
    filtered_addresses = df[(df['trashday'] == selected_day) & (df['zip_code'] == selected_zip)]

    if not filtered_addresses.empty:
        st.write(filtered_addresses)  # displays a table for all addresses with that day and zip code
    else:
        st.warning("Zip Code doesn't exist! Try another")  # if zip code is invalid, displays error message


def main():
    columns_to_read = ['full_address', 'mailing_neighborhood', 'zip_code', 'x_coord', 'y_coord', 'trashday', ]
    df = pd.read_csv('trashschedulesbyaddress.csv',
                     usecols=columns_to_read, )
    df_filtered = df.dropna().drop_duplicates(
        subset=['x_coord', 'y_coord'])  # filters out empty cells and duplicate buildings
    st.set_page_config(
        page_title="Boston Trash Collection App",
        initial_sidebar_state="expanded"
    )
    # sidebar for selecting page
    page = st.sidebar.selectbox("Select a page", ["Home", "Collection Map", "Collection Day Search",
                                                  "% of pickup days pie chart",
                                                  "Trash Pickup Days by Individual Neighborhood",
                                                  "Trash Pickup Days-all neighborhood comparison",
                                                  "Addresses by Pickup Day and Zip Code"])

    # page for trash collection map
    if page == "Home":

        st.markdown("<h1 style='text-align: center;'>Boston Trash Collection App</h1>", unsafe_allow_html=True)
        st.markdown(
            "<h2 style='text-align: center;'>This is an app that gives different tools to the user to display patterns "
            "with trash collection in Boston Neighborhoods.</h2>",  # description of the application
            unsafe_allow_html=True)
        st.image('Trash-Pickup.jpg')  # image for home page
    # runs each function depending on the page clicked on
    elif page == "Collection Map":
        plot_day_by_coordinates(df_filtered)
    elif page == "Collection Day Search":
        customer_pickup_day(df_filtered)
    elif page == "% of pickup days pie chart":
        display_trashday_piechart(df_filtered)
    elif page == "Trash Pickup Days by Individual Neighborhood":
        trash_day_by_mailing_neighborhood(df_filtered)
    elif page == "Trash Pickup Days-all neighborhood comparison":
        stacked_bar_by_neighborhood_and_day(df_filtered)
    elif page == "Addresses by Pickup Day and Zip Code":
        see_addresses_by_zip_and_day(df_filtered)


if __name__ == '__main__':
    main()
