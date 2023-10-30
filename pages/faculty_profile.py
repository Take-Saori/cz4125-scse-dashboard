import streamlit as st
from urllib.parse import urlparse, ParseResult
import ast
    
def link_button(display_string, link, use_container_width=False):
    # If link non nan,
    if not isinstance(link, float):
        st.link_button(display_string, link, use_container_width=use_container_width)
    # Else if link not available,
    else: 
        st.link_button(display_string, '', disabled=True, use_container_width=use_container_width)

st.title("Faculty Profile")

# If clicked on 'View profile'
if st.session_state.selected_faculty is not None:
    faculty_detail = st.session_state.selected_faculty

    col1, col2, col3 = st.columns([1,1,1])  # Divide the row into three columns

    with col1:
        st.image(faculty_detail['img_link'], width=200)

    with col2:
        st.write(f'Name: {faculty_detail["Name"]}')
        st.write(f'Email: {faculty_detail["Email"]}')

    with col3:
        pass

    tab1, tab2, tab3 = st.tabs(["Cat", "Dog", "External Links"])

    with tab1:
        st.header("A cat")
        st.image("https://static.streamlit.io/examples/cat.jpg", width=200)

    with tab2:
        st.header("A dog")
        st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

    with tab3:

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

# if did not click on view profile and got to profile page
else:
    st.error('Please select \'View Profile\' button in the Faculty List page to view faculty\'s details.')
