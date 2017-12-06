from utilities import id_list_to_string
from lookups import convert_county_identifier
from date_lookup import convert_month
import datetime


class FormatResource:
    """This takes data from the Information Center Database and organize it into the appropriate BLM Format. This
    The process requires multiple checks and conversions to fit our data into their style. Reformatted data is stored in
    self.formatted_resource dictionary, and can be retrieved by the get_resource method.

    :param prim_co: County identification of the primary number
    :param prim_no: Resource identification of the primary number
    :param tblResources: List of relevant data from the "tblResources" table of the ICDB
    """

    def __init__(self, prim_co, prim_no, tblResources, tblResourceIdent, tblResourceEvents):
        self.prim_co = prim_co
        self.prim_no = prim_no
        self.recording_events = tblResourceEvents

        self.formatted_resource = {
            "sTriState": "",
            "sTriCounty": "",
            "sTriNumber": "",
            "sTriSuffix": "",
            "sResourceType": self.decide_resource_type(tblResources),
            "sDistrictElement": self.convert_element_of_district(tblResources[8]),
            "sCollection": self.convert_collections_status(tblResources[9]),
            "sPeriod": self.convert_element_of_district(tblResources[8]),
            "sAgcyResourceID": self.convert_agency_name(tblResourceIdent),
            "sResourceName": self.convert_resource_name(tblResourceIdent),
            "dRecordedDate": self.recording_events[0][0]
        }

        self.validate_trinomial(tblResources)

    def validate_trinomial(self, rsrc_info):
        """Assure that the site qualifies for a trinomial, and calculate it."""
        if rsrc_info[0] is not None:
            self.formatted_resource["sTriState"] = "CA"
            self.formatted_resource["sTriCounty"] = convert_county_identifier("number", self.prim_co, "trinomial_code")
            self.formatted_resource["sTriNumber"] = self.prim_no
            self.formatted_resource["sTriSuffix"] = rsrc_info[1]

    @staticmethod
    def decide_resource_type(rsrc_info):
        """Decide which of the present resource types will be kept in BLM database."""
        if rsrc_info[6] is True:
            return "District"
        elif rsrc_info[5] is True:
            return "Site"
        elif rsrc_info[2] is True:
            return "Building"
        elif rsrc_info[3] is True:
            return "Structure"
        elif rsrc_info[4] is True:
            return "Object"
        elif rsrc_info[7] is True:
            return "Other"
        else:
            return ""

    @staticmethod
    def convert_element_of_district(element_status):
        """Convert boolean value to text"""
        if element_status is True:
            return "Y"
        else:
            return "N"

    @staticmethod
    def convert_collections_status(collection_status):
        conversion_dict = {"Yes": "Y", "No": "N", "Unknown": "U"}
        if collection_status is not None:
            return conversion_dict[collection_status]
        else:
            return "U"

    @staticmethod
    def decide_period(rsrc_info):
        """Decide which BLM time period best represents the IC defined classification"""
        if rsrc_info[11] is True:  # Checks Protohistoric
            return "B"
        elif all((rsrc_info[10], rsrc_info[12])):  # Checks both historic AND prehistoric
            return "B"
        elif rsrc_info[10] is True:
            return "P"
        elif rsrc_info[12] is True:
            return "H"
        else:
            return "U"

    @staticmethod
    def convert_agency_name(identifiers):
        # TODO: Figure out if NPS ID's should be redone as Nbr. Answer: They Should. Will be corrected soon (TM).
        appropriate_id_types = ["USFS", "BLM", "Agency Nbr"]
        return id_list_to_string(identifiers, appropriate_id_types)

    @staticmethod
    def convert_resource_name(identifiers):
        appropriate_id_types = ["Resource Name"]
        return id_list_to_string(identifiers, appropriate_id_types, titled=False)


class FormatReport:
    """This takes data from the Information Center Database and organize it into the appropriate BLM Format. This
    The process requires multiple checks and conversions to fit our data into their style. Reformatted data is stored in
    self.formatted_resource dictionary, and can be retrieved by the get_resource method.

    :param tblInventory: Contains title, organizational affiliation, and date information
    :param tblInventoryAuthor: Contains list of authors
    :param tblInventoryIdent: Contains list of report identifiers
    """

    def __init__(self, tblInventory, tblInventoryAuthor, tblInventoryIdent):
        print tblInventory
        print tblInventoryAuthor
        print tblInventoryIdent
        print
        self.formatted_report = {
            "sLeadAgencyNum": self.decide_identifiers(tblInventoryIdent),
            "sSurveyOrg": self.confirm_not_none(tblInventory[0]),
            "sAuthor": self.convert_authors(tblInventoryAuthor),
            "sReportTitle": self.confirm_not_none(tblInventory[1]),
            "dReportDte": self.convert_date(tblInventory[2], tblInventory[3])
        }

    @staticmethod
    def decide_identifiers(identifiers):
        """Converts agency identifiers into a list"""
        appropriate_id_types = ["BLM", "Caltrans", "USFS", "Agency Nbr", "CAL FIRE", "NRCS"]
        return id_list_to_string(identifiers, appropriate_id_types)

    @staticmethod
    def convert_authors(authors):
        """Convert list of author tuples to string"""
        author_list = ""
        multiple_authors = False
        for name in authors:
            if multiple_authors is True:
                author_list += '; '
            author_list += name[0]
            multiple_authors = True
        return author_list

    @staticmethod
    def convert_date(month, year):
        """Convert month and year to datetime object set on the first day of the month."""
        if month != '' and month is not None and year is not None:
            month = convert_month("abbreviation", month, "number")
            return datetime.date(year, month, 1)
        else:
            pass

    @staticmethod
    def confirm_not_none(field):
        if field is None:
            return ""
        else:
            return field
