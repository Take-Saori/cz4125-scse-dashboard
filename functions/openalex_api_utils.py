import json
import urllib
from urllib.request import urlopen
from urllib.error import HTTPError
from collections import Counter

import functions.utils as utils
import functions.dr_ntu_utils as dr_ntu


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


def get_author_stats(selected_faculty, faculty_api_id):
    """
    Return dictionary of selected_faculty from API.

    Input:
    - selected_faculty (pd.Series): Faculty detail from the csv.

    Output:
    - info_dict (Dictionary): Dictionary of faculty's detail.
                              Return None if faculty's API id cannot be retrieved.
    """

    
    author_details = get_author_info_from_OpenAlexAPI(selected_faculty['Name'],
                                                      faculty_api_id,
                                                      'api_id')

    info_dict = {}

    # Get all tags with score larger than 50
    tag_list = []
    for concept in author_details['x_concepts']:
        # If tag score is higher than 50 and the tag is not at top level
        if concept['score'] > 50 and not (concept['level'] == 0):
            tag_list.append(concept)
            
    info_dict['tags'] = tag_list

    # Get h_index
    info_dict['h_index'] = author_details['summary_stats']['h_index']

    # Get i10_index
    info_dict['i10_index'] = author_details['summary_stats']['i10_index']

    # Get work count and citation count for each year
    info_dict['counts_by_year'] = author_details['counts_by_year']

    # Get the last update
    info_dict['updated_date'] = author_details['updated_date']

    # Get the work count
    info_dict['works_count'] = author_details['works_count']

    return info_dict


def get_author_pubs_from_OpenAlexAPI(author_id, pub_num, sort_by=[], sort_direction='asc'):
    """
    Return a specified no. of publications' details from a specified author.

    Input:
    - author_id (string): Unique author ID, from OpenAlex API.
    - pub_num (int): No. of publications' details to return
    - sort_by (List(string)): To indicate how to sort the results from the API.
                              The sorting will be prioritized by the list order.
                              eg. If ['publication_date', 'display_name'],
                              then 'publication_date' will be used to sort first, followed by 'display_name'.
    - sort_direction (string): To indicate to sort the result in ascending or descending.
                               - If 'desc', sort by descending order.
                               - Otherwise, sort by ascending order.

    Output:
    - pub_list ( List(Dict) ): List of publications with each of their details written in dictionary format.
    """
    
    # Keys to remove from each publication details
    keys_to_remove = [
        'display_name',
        'language',
        'primary_location',
        'open_access',
        'countries_distinct_count',
        'institutions_distinct_count',
        'corresponding_author_ids',
        'corresponding_institution_ids',
        'apc_list',
        'apc_paid',
        'has_fulltext',
        'fulltext_origin',
        'is_retracted',
        'is_paratext',
        'concepts',
        'mesh',
        'locations_count',
        'best_oa_location',
        'sustainable_development_goals',
        'grants',
        'referenced_works_count',
        'ngrams_url',
        'abstract_inverted_index',
        'cited_by_api_url'
    ]

    pub_list = []
    
    query_url = 'https://api.openalex.org/works?filter=author.id:' + author_id

    if not sort_direction == 'desc':
        sort_direction = ''

    if not len(sort_by) == 0:
        query_url = query_url + '&sort='

    # Add the sorting requrements to the query API
    for i in range(len(sort_by)):
        # If the current sort is not the last element
        if not i == len(sort_by)-1:
            query_url = query_url + sort_by[i] + ':' + sort_direction + ','
        else:
            query_url = query_url + sort_by[i] + ':' + sort_direction

    # If pub_num is within range of "results per page range limits" given by the API,
    # request to get all results in one page
    if 1 <= pub_num <= 200:
        per_page = pub_num
    else:
        per_page = 200

    # Count to track the page number of the results
    page = 1
    
    while (len(pub_list) < pub_num):
        # Get results from the API
        try:
            response = urlopen(query_url + '&per-page=' + str(per_page) + '&page=' + str(page))
            response_json = json.loads(response.read())
            
            # Add the pub details to the list
            pub_list.extend(response_json['results'])
    
            # If all results available from the API is already stored,
            # stop querying
            if len(pub_list) == response_json['meta']['count']:
                break
            
            # Else, go to next page
            page += 1

        # Most likely did too much request, so HTTP 403 Forbidden
        except:
            # So stop querying and use only the results that are obtained earlier
            break

    for pub_dict in pub_list:
        for key in keys_to_remove:
            pub_dict.pop(key, None)

    return pub_list


def get_collab_info(faculty_id, faculty_pub_list):
    """
    Return list of authors who collaborated with a faculty for publication.
    (The faculty themself will not be included in this list.)
    The list will be in this format (and will refer to this list as result_list):
    [collab_author_name, collab_author_api_id, is_scse, pub_id_list, collab_count]

    - collab_author_name (string) will be the name of the collaborated author.
    - collab_author_api_id (string) is the OpenAlex API id of the collaborated author.
    - pub_id_list ( List(string) ) is the list of publication id (of OpenAlex API) that the author has collaborated with the faculty.
    - collab_count (int) is the no. of times the author has collaborated with this faculty.

    Input:
    - faculty_id (string): Faculty's API id.
    - faculty_pub_list ( List(string) ): List of publication details of a faculty.

    Output:
    - sorted_result ( List(List(string)) ): The list that contains a result_list for each collaborated authors.
    """
    
    # Dictionary to store the all collaborated author's info
    author_data = {}

    for data in faculty_pub_list:
        # Get the 'id' and 'display_name' of the author
        author_id = data['authorships'][0]['author']['id'].split('https://openalex.org/')[1]
        author_name = data['authorships'][0]['author']['display_name']

        if 'orcid' in data['authorships'][0]['author']:
            orcid_id = data['authorships'][0]['author']['orcid']
        else:
            orcid_id = None

        if 'institutions' in data['authorships'][0]:
            if len(data['authorships'][0]['institutions']) > 0:
                institution = data['authorships'][0]['institutions'][0]['display_name']
        else:
            institution = None
    
        # Get the 'id' of the work
        work_id = data['id'].split('https://openalex.org/')[1]
    
        if author_id == faculty_id:
            continue
    
        # Check if the author_id is already in the author_data dictionary
        if author_id in author_data:
            # Append the work_id to the existing list
            author_data[author_id][2].append(work_id)
        else:
            # Create a new entry for the author
            author_data[author_id] = [author_name, author_id, [work_id]]
    
    # Create the final list with the required format
    result_list = []
    for author_id, (author_name, _, work_ids) in author_data.items():
        result_list.append([author_name, author_id, orcid_id, institution, work_ids, len(work_ids)])

    # Sort list according to the no. of times the author has collaborated with the author (descending),
    # and alphabetic order of the collaborated author's name
    sorted_result = sorted(result_list, key=lambda x: (x[5], x[0]), reverse=True)

    return sorted_result


def get_journal_frequency(faculty_pub_list):
    """
    Return list of tuples that contains the name of journal and the frequency of the journal appearing in faculty_pub_list.
    The tuples will be sorted by the frequency in descending order, then alphabetic order by the journal name.

    Input:
    - faculty_pub_list ( List(string) ): List of publication details of a faculty.

    Output:
    - sorted_journal_counts ( List( tuple(string) )): List of tuples containing the name of journal and the frequency of it.
                                                      It will be in the form of:
                                                      [ (journal_1_name, journal_1_frequency),  (journal_2_name, journal_2_frequency), ...]

    """

    journal_counts = Counter()

    for entry in faculty_pub_list:
        locations = entry.get('locations', [])
        for location in locations:
            source = location.get('source')
            if source:
                source_type = source.get('type')
                if source_type == 'journal':
                    journal_name = source.get('display_name')
                    if journal_name:
                        journal_counts[journal_name] += 1

    # Sort the result by frequency (descending) and then by journal name (ascending)
    sorted_journal_counts = sorted(
        journal_counts.items(),
        key=lambda x: (-x[1], x[0])
    )

    return sorted_journal_counts