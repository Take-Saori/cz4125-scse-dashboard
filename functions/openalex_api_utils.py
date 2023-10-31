import json
import urllib
from urllib.request import urlopen
from urllib.error import HTTPError

import utils
import dr_ntu_utils as dr_ntu


def get_api_result(query_url):
    """
    Return API result by using query_url.

    Input:
    - query_url (string): URL to query to API.

    Output:
    - result (Dict): Dictionary of results from the API.
                     If error occurs, return the error details.
    """
    try:
        response = urlopen(query_url)
        result = json.loads(response.read().decode('utf-8'))
        return result
    except HTTPError as e:
        # Handle any HTTP error by returning a custom error message
        return {"error": f"HTTP error {e.code}: {e.reason}"}
    

def get_author_info_from_OpenAlexAPI(author_name, keyword, mode):
    """
    Return the dictionary of details of a specified author of the publication with specified doi.
    
    Input:
    - author_name (string): Name of the author retrieved from DR-NTU.
                            It will not be used when mode='orcid', as only the keyword is needed in that mode.
    - keyword (string): Term related to the author, which is used to search the author's details.
                        When mode='institution', keyword will not be used as the instituion ID (of NTU),
                        which is needed for this mode, will be defined in this function. Hence, it will
                        be usually left as an empty string for that mode.
    - mode (string): To indicate search method of author.
                     - if 'api_id', search author based on author's OpenAlex id.
                     - if 'doi', search author based on name and Digital Object Identifier (DOI) of a publication,
                       with author_name as one of the authors.
                     - if 'orcid', search author based on their ORCID profile link.
                     - if 'pub', search author based on name and publication title written by the author.
                     - if 'institution', search author based on last institution, name and x_concept.
                     - if 'name', search author based on name and x_concept.

    Output:
    - author_info (dict): Dictionary containing the details of the author by OpenAlex API.
    """
    
    if mode == 'api_id':
        query_url = 'https://api.openalex.org/authors/' + keyword
        author_info = get_api_result(query_url)            
        return author_info
        
    elif mode == 'doi':
        # API Query to search for pub with the specified doi
        query_url = "https://api.openalex.org/works/https://doi.org/" + keyword
        # print(query_url)
        result = get_api_result(query_url)

        # If API gave error
        if 'error' in result:
            return result

        # If no authors written
        if len(result['authorships']) == 0:
            return []
    
        authors_list = []
    
        # Get all authors' name
        for author in result['authorships']:
            authors_list.append(author['author']['display_name'])
    
        # Compare the names with author_name and get the index with the highest similarity
        similar_index = utils.get_most_similar_index(author_name, authors_list)
        author_info = result['authorships'][similar_index]

        return author_info

    elif mode == 'orcid':
        # Get details by ORCID id
        query_url = "https://api.openalex.org/authors/" + keyword
        # print(query_url)
        author_info = get_api_result(query_url)            
        return author_info

    elif mode == 'pub':
        # Get details by searching with publication title
        
        # Convert the name for query url
        query_converted_pub = urllib.parse.quote_plus(keyword)
        query_url = "https://api.openalex.org/works?search=" + query_converted_pub
        # print(query_url)
        result = get_api_result(query_url) 

        # If API gave error
        if 'error' in result:
            return result

        # If no results or no authors written
        if len(result['results']) == 0 or len(result['results'][0]['authorships']) == 0:
            return []

        authors_list = []
    
        # Get all authors' name from the first candinate publication only
        for author in result['results'][0]['authorships']:
            authors_list.append(author['author']['display_name'])
    
        # Compare the names with author_name and get the index with the highest similarity
        similar_index = utils.get_most_similar_index(author_name, authors_list)
        author_info = result['results'][0]['authorships'][similar_index]

        return author_info

    elif mode == 'institution':
        # Get details by last institution

        # Convert the name for query url
        query_converted_name = urllib.parse.quote_plus(author_name)
        
        query_url = 'https://api.openalex.org/authors?search=' + query_converted_name \
                    + '&filter=last_known_institution.id:I172675005,' \
                    + 'x_concepts.id:C41008148&sort=relevance_score:desc'
        result = get_api_result(query_url)
        # print(query_url)

        # If API gave error
        if 'error' in result:
            return result

        # If no results
        if len(result['results']) == 0:
            return []

        for candinate in result['results']:
            # Check if the author is relevant to 'Computer Science'
            for tag in candinate['x_concepts']:
                if tag['display_name'] == 'Computer science':
                    if tag['score'] > 70:
                        author_info = candinate
                        return author_info
                    else:
                        continue
                    
        # If no possible candinate
        return []

    else: # mode == 'name'
        # Get details by name only
        # This should be used only when no other option is viable
        
        # Convert the name for query url
        query_converted_name = urllib.parse.quote_plus(author_name)
        
        # x_concepts.id for 'Computer science' included in url
        query_url = 'https://api.openalex.org/authors?search=' + query_converted_name \
                    + '&filter=x_concepts.id:C41008148&sort=relevance_score:desc'
        result = get_api_result(query_url)
        # print(query_url)

        # If API gave error
        if 'error' in result:
            return result

        # If no results
        if len(result['results']) == 0:
            return []

        for candinate in result['results']:
            # Check if the author is relevant to 'Computer Science'
            for tag in candinate['x_concepts']:
                if tag['display_name'] == 'Computer science':
                    if tag['score'] > 70:
                        author_info = candinate
                        return author_info
                    else:
                        continue

        # If no possible candinate
        return []


def get_api_id_and_method(selected_faculty):
    """
    Return OpenAlex API id of selected_faculty and the method of retrieval of their details.

    Input:
    - selected_faculty (pd.Series): Faculty detail from the csv.

    Output:
    There will be two outputs wrapped in tuple: (OpenAlex_API_id, method).
    - OpenAlex_API_id (string): OpenAlex API id of selected_faculty.
                                If not available, return float('nan').
    - method (string): The method of retrieval of their details.
                       If OpenAlex_API_id was not available, return None.
    """

    # If the faculty has an ORCID link, get details based on that
    if isinstance(selected_faculty['orcid_link'], str):
        author_details = get_author_info_from_OpenAlexAPI(selected_faculty['Name'],
                                                          selected_faculty['orcid_link'],
                                                          'orcid')

        # If API did not give error
        if not 'error' in author_details:
            authorID = author_details['id'].split('https://openalex.org/')[1]
            return authorID, 'orcid'



    # If no ORCID or have ORCID but not in API, run the below codes

    # Retrieve the doi from dr-ntu site
    doi_list = dr_ntu.get_doi_list_from_drNTU(selected_faculty['dr_ntu_link'])

    # If DOI obtained, use that to search for the faculty in the API
    for doi in doi_list:
        author_details = get_author_info_from_OpenAlexAPI(selected_faculty['Name'], 
                                                          doi, 
                                                          'doi')
        
        # If API gave error, go to next DOI
        if 'error' in author_details:
            continue

        # Retrieve the author ID
        authorID = author_details['author']['id'].split('https://openalex.org/')[1]
        return authorID, 'doi'



    # If cannot retrieve any DOI or still have not found author, use publication title to search
    pub_list = dr_ntu.get_pub_list_from_article(selected_faculty['dr_ntu_link'])

    for pub in pub_list:
        author_details = get_author_info_from_OpenAlexAPI(selected_faculty['Name'], pub, 'pub')

        # If API gave error or no results, go to next pub
        if 'error' in author_details or len(author_details)==0:
            continue
            
        # Retrieve the author ID
        authorID = author_details['author']['id'].split('https://openalex.org/')[1]
        return authorID, 'pub'



    # If still have not found author, use name and institution to search
    author_details = get_author_info_from_OpenAlexAPI(selected_faculty['Name'], '', 'institution')

    # If API did not give error and have results
    if not ('error' in author_details or len(author_details)==0):
        authorID = author_details['id'].split('https://openalex.org/')[1]
        return authorID, 'institution'



    # If still have not found author, use name only to search
    author_details = get_author_info_from_OpenAlexAPI(selected_faculty['Name'], '', 'name')

    # If API did not give error and have results
    if not ('error' in author_details or len(author_details)==0):
        authorID = author_details['id'].split('https://openalex.org/')[1]
        return authorID, 'name'

        

    # If really cannot find faculty, set 'nan' for openAlex_authorID
    return float('nan'), None