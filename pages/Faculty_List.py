import streamlit as st
import pandas as pd
import math
from streamlit_extras.switch_page_button import switch_page

def pagination_prev():
    if st.session_state.current_page > 0:
        st.session_state.current_page -= 1

def pagination_next():
    if st.session_state.current_page < max_pages - 1:
        st.session_state.current_page += 1

# Load your faculty data
faculty_data = pd.read_csv('small_updated_csv_2.csv')


# Set page size and current page
page_size = 25
# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

if 'selected_faculty' not in st.session_state:
    st.session_state.selected_faculty = None

st.header("Faculty List")

# Sorting options
sort_order = st.selectbox('Sort by Name', ['Ascending', 'Descending'])
if sort_order == 'Ascending':
    faculty_data = faculty_data.sort_values(by='Name', ascending=True)
else:
    faculty_data = faculty_data.sort_values(by='Name', ascending=False)

# Search bar
search_term = st.text_input('Search Faculty by Name').lower()

# Filter faculty based on search term
filtered_data = faculty_data[faculty_data['Name'].str.lower().str.contains(search_term)]

# Calculate the maximum number of pages required
max_pages = math.ceil(len(filtered_data) / page_size)

# Ensure the current page is within the valid range
current_page = max(0, min(st.session_state.current_page, max_pages - 1))

# Enable or disable Previous and Next buttons
previous_button_enabled = current_page > 0
next_button_enabled = current_page < max_pages - 1

# Show both Previous and Next buttons
previous_key = f"previous_{current_page - 1}" if previous_button_enabled else None
next_key = f"next_{current_page + 1}" if next_button_enabled else None



# Create a row with three columns for the buttons and current page
col1, col2, col3 = st.columns([1,1,1])

with col1:
    st.button("Previous", on_click=pagination_prev, disabled=not previous_button_enabled, use_container_width=True)
with col2:
    st.write(f"Page {st.session_state.current_page + 1} / {max_pages}")
with col3:
    st.button("Next", on_click=pagination_next, disabled=not next_button_enabled, use_container_width=True)


# Paginate faculty list
start_idx = current_page * page_size
end_idx = start_idx + page_size
faculty_page = filtered_data.iloc[start_idx:end_idx]

st.write('---')  # Add a separator
# Create faculty cards
for index, row in faculty_page.iterrows():
    col1, col2, col3 = st.columns([1, 4, 1])  # Divide the row into three columns

    with col1:
        st.image(row['img_link'], width=100)

    with col2:
        st.write(f'Name: {row["Name"]}')
        st.write(f'Email: {row["Email"]}')
        button_key = f"view_profile_{row['Name']}"  # Unique key for each faculty
        if st.button('View Profile', key=button_key):
            # Set the selected faculty
            selected_faculty = row

    with col3:
        pass  # Spacer column

    st.write('---')  # Add a separator


st.session_state['selected_faculty'] = selected_faculty

# def click_profile(selected_faculty):
#     switch_page('faculty profile')

# Faculty profile page
if selected_faculty is not None:
    switch_page('faculty profile')