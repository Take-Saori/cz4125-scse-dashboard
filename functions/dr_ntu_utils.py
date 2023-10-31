import bs4 # imported to compare if certain bs4 object are a certain bs4 type
from bs4 import BeautifulSoup
import requests
import re

from functions import utils

def get_research_interest_from_drNTU(drNTU_link):
    """
    Return the list of tags of the researcher in their DR-NTU page.

    Input:
    - drNTU_link (string): DR-NTU profile URL of a SCSE faculty.

    Output:
    - tag_list (List(string)) : List of research interest found on DR-NTU profile page of that faculty.
    """
    soup_source = requests.get(drNTU_link).text
    soup = BeautifulSoup(soup_source,'lxml')

    tag_list = []

    for tag in soup.find('div', id='taxonomyDiv', class_='dynaFieldValue').find_all('span', class_='rkeyword'):
        tag_name = tag.text.strip()
        if not tag_name == 'Computer Science and Engineering':
            tag_list.append(tag_name)
    
    return tag_list


# From Individual Assignment 1
def get_cleaned_pub_list(unprocessed_pub_list):
    """
    Return list of cleaned publication citation from the unprocessed_pub_list retrieved
    from the DR-NTU profile publication tab.

    Input:
        - unprocessed_pub_list (list): List of publication details extracted by BeautifulSoup.
                                       It also contains elements that are tags, without any text.
    """
    
    # Initialize variables
    cleaned_pub_list = []
    current_subset = []
    
    # To keep track of the number of consecutive <br/> elements
    # Because each publication can be splitted by 2 consecutive <br/> elements
    br_count = 0
    
    # Iterate through the unprocessed_pub_list
    for item in unprocessed_pub_list:
        
        # Check if the item is a string or a BeautifulSoup object
        if isinstance(item, str):
            # If it is a string, add it to the current_subset
            current_subset.append(item)
            
        elif str(item) != '<br/>':
            # If it is a BeautifulSoup object and not <br/>, convert it to a string and add it to the current_subset
            current_subset.append(str(item))
    
        # Check if the current item is a <br/>
        if str(item) == '<br/>':
            br_count += 1
            if br_count == 2:
                # If two consecutive <br/> tags are found,
                # concatenate the current subset and reset it
                cleaned_pub_list.append(''.join(current_subset))
                
                # Empty current_subset to store the next subset
                current_subset = []
                
            elif br_count > 2:
                # If more than 2 consecutive <br/> tags are found, reset the count
                br_count = 1
    
    # Append the last subset if there are remaining elements
    if current_subset:
        cleaned_pub_list.append(''.join(current_subset))

    # Remove the subsets that are not publication citations
    remove_list = ['<br/>', 'Highly Cited:', 'Click', 'Recent Publication:']
    for remove_word in remove_list:
        cleaned_pub_list[:] = [subset for subset in cleaned_pub_list if remove_word not in subset]

    # Remove element that is a empty string
    cleaned_pub_list[:] = [subset for subset in cleaned_pub_list if not subset == '']

    # Remove the tags in the citations
    replace_list = ['<b>', '</b>', '<i>', '</i>']
    for replace_word in replace_list:
        cleaned_pub_list[:] = [subset.replace(replace_word, '') for subset in cleaned_pub_list]
    
    return cleaned_pub_list


def get_unprocessed_pub_list(drNTU_link):
    """
    Return publication details from DR-NTU faculty's profile in publication tab.

    Input:
    -  drNTU_link (string): DR-NTU profile link (in publication tab) of a SCSE faculty.

    Output:
    - unprocessed_pub_list (list): List of publication details extracted by BeautifulSoup.
                                       It also contains elements that are tags, without any text.
    """

    # print(drNTU_link+'/selectedPublications.html')
    soup_source = requests.get(drNTU_link+'/selectedPublications.html').text
    soup = BeautifulSoup(soup_source,'lxml')

    # If "Articles (Journal)" tab does not exist for this faculty,
    # return an empty list
    if not soup.find('div', id="facultyjournalDiv"):
        return []
    
    # Get publication list from the profile page, but unprocessed
    unprocessed_pub_list = soup.find('div', id="facultyjournalDiv").contents[1].contents

    return unprocessed_pub_list


def get_doi_list_from_drNTU(drNTU_link):
    """
    Return the list of DOI of all publications written by the researcher, in their DR-NTU page.

    Input:
    - drNTU_link (string): DR-NTU profile link (in publication tab) of a SCSE faculty.

    Output:
    - doi_list (List(string)) : List of DOI found on DR-NTU publication page of that faculty.
    """

    doi_list = []
    
    # Get publication list from the profile page, but unprocessed
    unprocessed_pub_list = get_unprocessed_pub_list(drNTU_link)

    # Get the processed version of the publication 
    cleaned_pub_list = get_cleaned_pub_list(unprocessed_pub_list)

    # Regex to extract DOI
    doi_pattern = r'doi:\s+(\S+)'

    for pub in cleaned_pub_list:
        match = re.search(doi_pattern, pub)

        if match:
            doi_list.append(match.group(1))

    return doi_list


# Modified code from Assignment 1
def get_pub_list_from_article(drNTU_link):
    """
    Return list of all publication with title only, from the "Articles (Journal)" tab if it exist

    <pub_1_title> will not be appended if <pub_1_title> was not correctly extracted by regex.

    Input:
    - dr_ntu_pub_link (string): DR-NTU profile link (in publication tab)

    Output:
    - pub_title_list (List(string)): List of publication extracted from faculty's profile in publication tab.
    """

    # List to store list of publication title and year.
    pub_title_list = []
    
    # Get publication list from the profile page, but unprocessed
    unprocessed_pub_list = get_unprocessed_pub_list(drNTU_link)

    # Get the processed version of the publication 
    cleaned_pub_list = get_cleaned_pub_list(unprocessed_pub_list)
    
    # Extract title and year from all the publications
    for pub in cleaned_pub_list:
        one_pub_title = get_one_pub_title(pub)
        
        # If title was retrieved
        if one_pub_title:
            # If the title have at least 3 words,
            # append to the list
            if utils.have_words(one_pub_title, 3):
                pub_title_list.append(one_pub_title)

    return pub_title_list


# Modified code from Assignment 1
def get_one_pub_title(pub_citation):
    """
    Return publication title for one publication citation.
    The citation will not be a full citation. 
    Return None if title could not be retrieved.

    Input:
    - pub_citation (string): Citation of a paper retrieved from publication tab
                              in DR-NTU profile page of a SCSE faculty.

    Output:
    - pub_title (string): Title of the publication retrieved from the citation.
    """
    
    # If there is double inverted commas in the citation, that is the title.
    # So get the title between the double inverted commas
    if '"' in pub_citation or '“' in pub_citation or '”' in pub_citation:
        # Replace the other variation of double inverted commas
        # to the default ones
        pub_citation = pub_citation.replace("“", '"').replace("”", '"')

        # Extract the title and year (if exist)
        pub_title = re.findall(r'"(.*?)"', pub_citation)[0]
        
        return pub_title

    # For papers that do not have double inverted commas:
    pattern = r'(\d{4}),*\s*\w*[),.]+\s*(.*?)[,.]'
    matches = re.findall(pattern, pub_citation)

    # If no match found
    if len(matches) == 0: 
        return None

    # If match found
    pub_title = matches[0][1]

    return pub_title