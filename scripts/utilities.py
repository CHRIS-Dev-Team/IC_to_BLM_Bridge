def id_list_to_string(identifiers, appr_id_types=[], do_all=False, titled=True):
    """Takes the list of individual identifiers and groups them by type. Then it converts that dictionary into a string
    and removes any left over syntax.

    :param identifiers: The list of identifiers as pulled from the ICDB.
    :param appr_id_types: The identifier types that will be output. Uses the identifier types from the ICDB.
    Empty list by default.
    :param do_all: If true, this will override the appr_id_types and add all identifiers together.
    This is False by default.

    :return: Returns a string where ID's are grouped by type.
    """

    id_list = {}

    if (appr_id_types == [] or appr_id_types is None) and do_all is False:
        raise Exception("Parameters Incorrectly Set: \n\n\n"
                        "    appr_id_types is \"{}\" but should be a list with ICDB name types. \n\n"
                        "        --or-- \n\n"
                        "    do_all is set to \"False\" and should be set to "
                        "\"True\" if you wish to merge all name types.".format(appr_id_types))
    else:
        for identifier in identifiers:
            if identifier[0] in appr_id_types or do_all is True:
                id_list[str(identifier[0])] = ''

        for id_type in id_list:
            for identifier in identifiers:
                if id_type == str(identifier[0]):
                    if len(id_list[id_type]) > 0:
                        id_list[id_type] += ", "
                    id_list[id_type] += str(identifier[1])

        output = ''
        for key in id_list:
            if titled is True:
                output += "{}: {}; ".format(key, id_list[key])
            else:
                output += id_list[key]

        return output[:-2]
