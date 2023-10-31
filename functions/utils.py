from thefuzz import process

def get_most_similar_index(find_string, string_list):
    """
    Return the index of the string (in string_list), that is the most similar with find_string.

    Input:
    - find_string (string): String to find in string_list.
    - string_list (List(string)): List of strings.

    Output:
    - similar_index (int): Index of the string (in string_list) that is most similar to find_string.
                           If there is no string that is at least 70% similar to find_string,
                           return None.
    """

    # Get the name that is most similar
    similar_name, _ = process.extractOne(find_string, string_list)
    similar_name_index = string_list.index(similar_name)

    return similar_name_index


def have_words(input_string, at_least_num):
    """
    Return True if the string contains at least at_least_num words.
    Return False otherwise.

    Input:
    - input_string (string): String to count the no. of words.
    - at_least_num (int): Number of words the string should at least contain,
                    to return True.
    """
    
    # Split the string into words using spaces as the delimiter
    words = input_string.split()
    
    # Check if the no .of words is at least at_least_num
    if len(words) >= at_least_num:
        return True
    else:
        return False
    

def find_list_with_value(list_of_lists, target_value):
    """
    Return index of a list that contains the target value, from a list of lists.

    Input:
    - list_of_lists ( List( List(string) ) ): List of lists.
    - target_value (string): String to search for in the list of lists.

    Output:
    - index (int): Index of list that contains target_value.
                   If no list contains the target_value, return -1.

    """
    
    for index, sub_list in enumerate(list_of_lists):
        if target_value in sub_list:
            return index  # Return the index of the list containing the value
    return -1  # Return -1 if the value is not found in any list