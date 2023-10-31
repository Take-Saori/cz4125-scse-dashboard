import streamlit as st
from urllib.parse import urlparse, ParseResult
import ast
import pandas as pd
from datetime import datetime

import functions.openalex_api_utils as api_utils

    
def link_button(display_string, link, use_container_width=False):
    # If link non nan,
    if isinstance(link, str):
        st.link_button(display_string, link, use_container_width=use_container_width)
    # Else if link not available,
    else: 
        st.link_button(display_string, '', disabled=True, use_container_width=use_container_width)

def convert_to_alphabet_date(input_date):
    try:
        # Convert the string to a datetime object
        date_object = datetime.strptime(input_date, "%Y-%m-%dT%H:%M:%S.%f")

    except:
        # Convert the string to a datetime object
        date_object = datetime.strptime(input_date, "%Y-%m-%d")

    # Format the date in the desired format (DD MM YYYY)
    formatted_date = date_object.strftime("%d %B %Y")

    return formatted_date

def print_pubs(pub_list):
    for i in range(len(pub_list)):
        st.write(f'{i+1}. **{pub_list[i]["title"]}**')
        st.write(f'- Published date: {convert_to_alphabet_date(pub_list[i]["publication_date"])}')
        st.write(f'- No. of citations: {pub_list[i]["cited_by_count"]}')
        
        if 'locations' in pub_list[i]:
            if len(pub_list[i]['locations']) > 0:
                for j in range(len(pub_list[i]['locations'])):
                    if 'source' in pub_list[i]['locations'][j]:
                        if pub_list[i]['locations'][j]["source"]:
                            if j == 0:
                                st.write('- Published in:')
                            st.write(f'----- {pub_list[i]["locations"][j]["source"]["display_name"]}')
        if isinstance(pub_list[i]["doi"], str):
            st.link_button('View Publication', pub_list[i]["doi"])
        st.text('')

st.title("Faculty Profile")
st.write('---')  # Add a separator

# If clicked on 'View profile'
if st.session_state.selected_faculty is not None:

    faculty_detail = st.session_state.selected_faculty

    col1, col2, col3 = st.columns([1,1,1])  # Divide the row into three columns

    with col1:
        st.image(faculty_detail['img_link'], width=200)

    with col2:
        st.subheader(faculty_detail["Name"])
        st.write(f'Email: {faculty_detail["Email"]}')

    with col3:
        pass

    tab1, tab2, tab3, tab4 = st.tabs(["Interests", "Publications", "Collaborated Authors", "External Links"])

    if not st.session_state.faculty_api_id:
        faculty_api_id, retrieve_method = api_utils.get_api_id_and_method(faculty_detail)
        st.session_state.faculty_api_id = faculty_api_id
        st.session_state.retrieve_method = retrieve_method

    if st.session_state.retrieve_method:
        if not st.session_state.faculty_info:
            st.session_state.faculty_info = api_utils.get_author_stats(faculty_detail, st.session_state.faculty_api_id)

        with tab2:
            st.write(f'Last updated: {str(convert_to_alphabet_date(st.session_state.faculty_info["updated_date"]))}')
            st.write('---')  # Add a separator

            st.subheader('No. of works and citations in past 10 years')

            col1, col2 = st.columns([2,1])

            with col1:
                pub_stats_df = pd.DataFrame(st.session_state.faculty_info['counts_by_year']).sort_values(by='year')
                pub_stats_df['year'] = pub_stats_df['year'].astype(str).str.replace(',', '')
                pub_stats_df.rename(columns={'year': 'Year', 'works_count': 'No. of works', 'cited_by_count': 'No. of citations'},
                                    inplace=True)
                st.line_chart(pub_stats_df,
                            x="Year", y=["No. of works", "No. of citations"], color=["#FF0000", "#0000FF"])
            with col2:
                st.markdown(f'h index: {str(st.session_state.faculty_info["h_index"])}',
                            help='The h-index is calculated by counting the number of publications \
                                    for which an author has been cited by other authors at least that same \
                                    number of times. For instance, an h-index of 17 means that the scientist \
                                    has published at least 17 papers that have each been cited at least 17 times.\
                                    \n(Extracted from: https://mdanderson.libanswers.com/faq/26221#:~:text=The%20h%2Dindex%20is%20calculated,cited%20at%20least%2017%20times.)')
                st.markdown(f'i-10 index: {str(st.session_state.faculty_info["i10_index"])}',
                            help='The i-10 index indicates the number of academic publications an author has \
                                written that have been cited by at least 10 sources.\
                                \n(Extracted from: https://en.wikipedia.org/wiki/Author-level_metrics)')
                st.markdown(f'Total no. of citations: {str(int(faculty_detail["citations_all_num"]))}',
                            help='The total number of times the works of this faculty\'s is cited by others.')

            st.write('---')  # Add a separator
            st.subheader('Top 10 recent works')
            recent_pub_list = api_utils.get_author_pubs_from_OpenAlexAPI(st.session_state.faculty_api_id, 10,\
                                                                  sort_by=['publication_date'],\
                                                                  sort_direction='desc')
            print_pubs(recent_pub_list)

            st.write('---')  # Add a separator
            st.subheader('Top 10 cited works')
            cited_pub_list = api_utils.get_author_pubs_from_OpenAlexAPI(st.session_state.faculty_api_id, 10,\
                                                                  sort_by=['cited_by_count'],\
                                                                  sort_direction='desc')
            print_pubs(cited_pub_list)

        with tab1:
            st.write(f'Last updated: {str(convert_to_alphabet_date(st.session_state.faculty_info["updated_date"]))}')
            st.write('---')  # Add a separator

            col1, col2 = st.columns(2)

            with col1:
                # If there are tags from DR-NTU site
                if not isinstance(faculty_detail["Interests"], float):
                    st.subheader('Interests')
                    interests_list = ast.literal_eval(st.session_state.selected_faculty['Interests'])
                    for interest in interests_list:
                        st.write(interest)

            with col2:
                # If there are tags from the api, 
                if len(st.session_state.faculty_info['tags']) > 0:
                    st.subheader(f'Top topics based on {faculty_detail["Name"]} works')
                    for i in range(len(st.session_state.faculty_info['tags'])):
                        st.write(f'{i+1}. {st.session_state.faculty_info["tags"][i]["display_name"]}')

        with tab4:
            st.write(f'Last updated: {str(convert_to_alphabet_date(st.session_state.faculty_info["updated_date"]))}')
            st.write('---')  # Add a separator

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                link_button('DR-NTU Link', faculty_detail['dr_ntu_link'], True)

            with col2:
                link_button('ORCID Link', faculty_detail['orcid_link'], True)

            with col3:
                link_button('dblp Link', faculty_detail['dblp_link'], True)

            with col4:
                link_button('Google Scholar Link', faculty_detail['google_scholar_link'], True)

            st.write('---')  # Add a separator
            
            if not isinstance(st.session_state.selected_faculty['website_link'], float):
                weblinks = ast.literal_eval(st.session_state.selected_faculty['website_link'])

                # If other websites available, 
                if len(weblinks) > 0:
                    st.write('Other websites:')
                    i = 0
                    while i < len(weblinks):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            base_link = '.'.join(urlparse(weblinks[i]).netloc.split('.')[1:])
                            st.link_button(base_link, weblinks[i], use_container_width=True)
                            i+=1

                        with col2:
                            if i < len(weblinks):
                                base_link = '.'.join(urlparse(weblinks[i]).netloc.split('.')[1:])
                                st.link_button(base_link, weblinks[i], use_container_width=True)
                                i+=1
                            else:
                                break

                        with col3:
                            if i < len(weblinks):
                                base_link = '.'.join(urlparse(weblinks[i]).netloc.split('.')[1:])
                                st.link_button(base_link, weblinks[i], use_container_width=True)
                                i+=1
                            else:
                                break

                        with col4:
                            if i < len(weblinks):
                                base_link = '.'.join(urlparse(weblinks[i]).netloc.split('.')[1:])
                                st.link_button(base_link, weblinks[i], use_container_width=True)
                                i+=1
                            else:
                                break

        with tab3:
            st.write(f'Last updated: {str(convert_to_alphabet_date(st.session_state.faculty_info["updated_date"]))}')
            st.write('---')  # Add a separator

            st.subheader('Top 10 Collaborated Authors',
                         help='These author\'s worked on the same publication with faculty. These are the top 10\
                            authors who collaborated with the faculty the most in the recent works (the most 50 \
                            recent works).')
            if not st.session_state.collab_info:
                st.session_state.collab_info = api_utils.get_collab_info(st.session_state.faculty_api_id,
                                                        api_utils.get_author_pubs_from_OpenAlexAPI(st.session_state.faculty_api_id, 50,\
                                                                                                    sort_by=['publication_date'],\
                                                                                                    sort_direction='desc')
                                                                        )
            for i in range(10):
                st.write(f'{i+1}. {st.session_state.collab_info[i][0]}')
                st.write(f'- Number of times collaborated: {st.session_state.collab_info[i][4]}')
                if st.session_state.collab_info[i][2]:
                    st.link_button('ORCID Link', st.session_state.collab_info[i][2])
                with st.expander("Collaborated works"):
                    for j in range(len(st.session_state.collab_info[i][3])):
                        # Get name of work
                        query_url = 'https://api.openalex.org/works/' + st.session_state.collab_info[i][3][j]
                        collab_work_details = api_utils.get_api_result(query_url)
                        st.write(f'{j+1}. **{collab_work_details["title"]}**')
                        st.write(f'- Published date: {convert_to_alphabet_date(collab_work_details["publication_date"])}')
                        st.write(f'- No. of citations: {collab_work_details["cited_by_count"]}')
                        
                        if 'locations' in collab_work_details:
                            if len(collab_work_details['locations']) > 0:
                                for j in range(len(collab_work_details['locations'])):
                                    if 'source' in collab_work_details['locations'][j]:
                                        if collab_work_details['locations'][j]["source"]:
                                            if j == 0:
                                                st.write('- Published in:')
                                            st.write(f'----- {collab_work_details["locations"][j]["source"]["display_name"]}')
                        if isinstance(collab_work_details["doi"], str):
                            st.link_button('View Publication', collab_work_details["doi"])
                        st.text('')
            st.text('')
            




            
            
# if did not click on view profile and got to profile page
else:
    st.error('Please select \'View Profile\' button in the Faculty List page to view faculty\'s details.')
