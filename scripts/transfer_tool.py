"""
This code will be responsible for moving the features from the GIS specialist's personal geodatabase to
BLM's proxy database.
"""
import arcpy
import pypyodbc
from scripts.format_for_blm_proxy import FormatResource, FormatReport
from errors import add_header


class ToProxy:
    def __init__(self, source_db, target_db, project_boundaries, log):
        """This class will transfer points and lines resource features to the BLM Proxy database.

        :param source_db: The file address for the IC's GIS database
        :param target_db: The file address for the BLM's proxy database
        :param project_boundaries: The address for a project boundaries feature class.
            Must specify location within the geodatabase.
        """
        print "  Starting..."
        arcpy.env.workspace = source_db
        self.source_db = source_db
        self.project_boundaries = project_boundaries
        self.target_db = target_db
        self.proxy = ""
        self.icdb = None

    def send_resources_to_proxy(self, project_dist_buffer):
        """
        Iterates through the resource layers, selecting and processing each one.

        :param project_dist_buffer: distance and specified measurement unit abbreviation (ex. '.5 mi' or '2 km')
        :type project_dist_buffer: str
        """
        # layer_list = {"resource_points": 1, "resource_lines": 1, "resource_polys": 0, "resource_aprxloc": 0}
        layer_list = {"resource_polys": 0}
        self.proxy = "{}\{}\{}".format(self.target_db, "CRM_Resources", "res_inproc_proxy")
        for layer in layer_list:
            print "\n  Moving {}".format(layer)
            layer_address = "{}\Resources\{}".format(self.source_db, layer)
            self.select(layer, project_dist_buffer)
            if layer_list[layer] == 1:
                self.buffer("resource", layer, 15)
            else:
                self.move_resources(layer + '_selection', 0)
        self.merge_resources()

    def send_reports_to_proxy(self, project_dist_buffer):
        """
        Iterates through the report layers, selecting and processing each one.

        :param project_dist_buffer: distance and specified measurement unit abbreviation (ex. '.5 mi' or '2 km')
        :type project_dist_buffer: str
        """
        # layer_list = {"report_points": 1, "report_lines": 1, "report_polys": 0, " report_cfmou": 0, "report_aprxloc": 0}
        layer_list = {"report_polys": 0}
        self.proxy = "{}\{}\{}".format(self.target_db, "CRM_Investigations", "inv_inproc_proxy")
        for layer in layer_list:
            print "\n  Moving {}".format(layer)
            layer_address = "{}\Reports\{}".format(self.source_db, layer)
            self.select(layer, project_dist_buffer)
            if layer_list[layer] == 1:
                self.buffer("report", layer, 15)
            else:
                self.move_reports(layer + '_selection', 0)
        self.merge_reports()

    def select(self, layer_name, selection_buffer_distance):
        """Selects the features to be transferred. This is based on its location within the targeted quad,
        location within project area (BLM Lands with a mile buffer), and confirmation that the record hasn't been
        transferred already."""
        print "    Selecting..."
        selection_layer_name = layer_name + '_selection'
        arcpy.MakeFeatureLayer_management(layer_name, selection_layer_name)
        arcpy.SelectLayerByLocation_management(selection_layer_name,
                                               "WITHIN_A_DISTANCE",
                                               select_features=self.project_boundaries,
                                               search_distance=selection_buffer_distance)

    def buffer(self, document_type, layer_name, buffer_distance):
        """
        Applies a standard buffer to point and linear features.
        :param document_type: Resources or Reports
        :param layer_name: Name of the Information Center GIS layer
        :param buffer_distance: Buffer distance in meters. It will be the radius around a point, or distance applied to
            both side of a line.
        """
        print "    Buffering..."
        arcpy.Buffer_analysis(layer_name + "_selection", layer_name + "_bufsel", "{} Meters".format(buffer_distance))
        if document_type == "resource":
            self.move_resources(layer_name + '_bufsel', 1)
        elif document_type == "report":
            self.move_reports(layer_name + '_bufsel', 1)
        else:
            raise NameError("{} is not recognized as a valid document type."
                            "Please use 'resource' or 'report' when calling this method.")

    def move_resources(self, source_layer_name, buffer_type):
        """
        Moves the resource features to the proxy database.
        :param source_layer_name: Name of the layer that will be moved. (Either Selection or BufSelection)
        :param buffer_type: Specifies if the layer has been buffered or not. (1 is buffered, 0 for not)
        """
        # One of the following strings need to be added to the Append string, depending on if layer was buffered or not.
        buffer_settings = ["iBufferDist \"Buffer Distance\" true false false 2 Short 0 0 ,First,#;",
                           "iBufferDist \"Buffer Distance\" true false false 2 Short 0 0 ,First,#,{0},BUFF_DIST,-1,-1;".format(
                               source_layer_name)]
        print "    Moving shapes to proxy..."
        arcpy.Append_management(source_layer_name, self.proxy, "NO_TEST",
                                "sPCountyNum \"P # - County #\" true true false 2 Text 0 0 ,First,#,{0},PrimCo,-1,-1;"  # PrimCo
                                "sPNumber \"P # - Number\" true true false 30 Text 0 0 ,First,#,{0},PrimNo,-1,-1;"  # PrimNo
                                "{1}"  # The correct buffer string will be added here.
                                "sHPosSrce \"Horiz pos Source\" true true false 10 Text 0 0 ,First,#,{0},DigSource,-1,-1;"  # DigSource
                                "sDigNotes \"Digitizing Notes\" true true false 165 Text 0 0 ,First,#,{0},Notes,-1,-1;"  # Notes
                                "sDigBy \"Digitized By\" true true false 16 Text 0 0 ,First,#,{0},DigBy,-1,-1;"  # DigBy
                                "dDigDate \"Date Digitized\" true true false 8 Date 0 0 ,First,#,{0},DigDate,-1,-1;"  # Dig Date
                                .format(
                                    source_layer_name,
                                    buffer_settings[buffer_type]), "")

    def move_reports(self, source_layer_name, buffer_type):
        """
        Moves the reports features to the proxy database.
        :param source_layer_name: Name of the layer that will be moved. (Either Selection or BufSelection)
        :param buffer_type: Specifies if the layer has been buffered or not. (1 is buffered, 0 for not)
        """
        buffer_settings = ["iBufferDist \"Buffer Distance\" true false false 2 Short 0 0 ,First,#;",
                           "iBufferDist \"Buffer Distance\" true false false 2 Short 0 0 ,First,#,{0},BUFF_DIST,-1,-1;".format(
                               source_layer_name)]
        print "    Moving shapes to proxy..."
        arcpy.Append_management(source_layer_name, self.proxy, "NO_TEST",
                                "sSHPOTrackNum \"IC/SHPO Tracking #\" true true false 50 Text 0 0 ,First,#,{0},Label,-1,-1;"  # Label
                                "{1}"  # Buffer
                                "sDigNotes \"Notes\" true true false 165 Text 0 0 ,First,#,{0},Notes,-1,-1;"  # Notes
                                "sDigBy \"Digitized By\" true true false 16 Text 0 0 ,First,#,{0},DigBy,-1,-1;"  # DigBy
                                "dDigDate \"Date Digitized\" true true false 8 Date 0 0 ,First,#,{0},DigDate,-1,-1;"  # DigDate
                                "iQCStatus \"QC Status\" true true false 2 Short 0 0 ,First,#;"
                                "MODIFY_BY \"Last Modified By\" true true false 30 Text 0 0 ,First,#;"
                                "MODIFY_DATE \"Last Modify Date\" true true false 8 Date 0 0 ,First,#,{0},EditDate,-1,-1;"  # Edit Date
                                .format(
                                    source_layer_name,
                                    buffer_settings[buffer_type]), "")

    def connect_to_icdb(self):
        connection2 = pypyodbc.connect(
            "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            "UID=admin;UserCommitSync=Yes;Threads=3;SafeTransactions=0;PageTimeout=5"
            "MaxScanRows=8;MaxBufferSize=2048;FIL={MS Access};DriverId=25;"
            "DefaultDir=H:\\neicdata\\database\\main;"
            "DBQ=H:\\neicdata\\database\\main\\icdb_backend_neic_test.accdb;"
        )
        self.icdb = connection2.cursor()

    def merge_resources(self):
        """Iterates through the proxy database and merges shapes with the same PrimCo or PrimNo."""
        #  Make the following string formatted so that the layer appends from the
        #  FeatureLayer created by the select function.
        print "    Adding ICDB Data..."
        fields = ["sPCountyNum", "sPNumber", "sTriState", "sTriCounty", "sTriNumber", "sTriSuffix", "sResourceType",
                  "sDistrictElement", "sCollection", "sPeriod", "sAgcyResourceID", "sResourceName", "dRecordedDate"]
        self.connect_to_icdb()
        arcpy.env.workspace = self.target_db
        try:
            with arcpy.da.Editor(self.target_db) as edit:
                with arcpy.da.UpdateCursor(self.proxy, fields) as proxy_cursor:
                    for row in proxy_cursor:
                        # Main Data from tblResource
                        self.icdb.execute("SELECT TrinNo, TrinH, "
                                          "ResTypeBuilding, ResTypeStructure, ResTypeObject, "
                                          "ResTypeSite, ResTypeDistrict, ResTypeOther, ResTypeElement, "
                                          "ResourceCollections, "
                                          "AgePre, AgePro, AgeHist, AgeUnk "
                                          "FROM tblResource "
                                          "WHERE PrimCo = {} AND PrimNo = {}".format(row[0], row[1].zfill(6)))
                        tblResource = self.icdb.fetchone()
                        # Identifiers and Names from tblResourcesIdent
                        self.icdb.execute("SELECT IdentifierType, Identifier "
                                          "FROM tblResourceIdent "
                                          "WHERE PrimCo = {} AND PrimNo = {} ".format(row[0], row[1].zfill(6)))
                        tblResourceIdent = self.icdb.fetchall()
                        # Recording Dates from tblRescourceEvents
                        self.icdb.execute("SELECT FIRST(RecDate) "
                                          "FROM tblResourceEvents "
                                          "WHERE PrimCo = {} AND PrimNo = {} "
                                          "GROUP BY PrimCo, PrimNo".format(row[0], row[1].zfill(6)))
                        tblResourceEvent = self.icdb.fetchall()
                        try:
                            results = FormatResource(row[0], row[1].zfill(6), tblResource, tblResourceIdent,
                                                     tblResourceEvent)
                        except TypeError:
                            pass
                        position = 2
                        for field in fields[2:]:
                            row[position] = results.formatted_resource[field]
                            position += 1
                        try:
                            proxy_cursor.updateRow(row)
                        except RuntimeError, e:
                            print str(e)
                            print row

        except arcpy.ExecuteError:
            print arcpy.GetMessage(2)

    def merge_reports(self):
        fields = ["sSHPOTrackNum", 'sLeadAgencyNum', 'sSurveyOrg', 'sAuthor', 'sReportTitle', 'dReportDte']
        self.connect_to_icdb()
        arcpy.env.workspace = self.target_db
        try:
            with arcpy.da.Editor(self.target_db) as edit:
                with arcpy.da.UpdateCursor(self.proxy, fields) as proxy_cursor:
                    for row in proxy_cursor:
                        # Main Data from tblInventory
                        self.icdb.execute("SELECT CitPublisher, CitTitle, CitMonth, CitYear "
                                          "FROM tblInventory "
                                          "WHERE DocNo = {}".format(row[0]))
                        tblInventory = self.icdb.fetchone()
                        # Author Names from tblInventory Author
                        self.icdb.execute("SELECT DocAuthorText "
                                          "FROM tblInventoryAuthor "
                                          "WHERE DocNo = {}".format(row[0]))
                        tblInventoryAuthor = self.icdb.fetchall()
                        # Identifiers from tblResourcesIdent
                        self.icdb.execute("SELECT IdentifierType, Identifier "
                                          "FROM tblInventoryIdent "
                                          "WHERE DocNo = {}".format(row[0]))
                        tblInventoryIdent = self.icdb.fetchall()
                        results = FormatReport(tblInventory, tblInventoryAuthor, tblInventoryIdent)
                        position = 1
                        for field in fields[1:]:
                            row[position] = results.formatted_report[field]
                            position += 1
                        try:
                            proxy_cursor.updateRow(row)
                        except RuntimeError, e:
                            print str(e)
                            print row
        except arcpy.ExecuteError:
            print arcpy.GetMessage(2)

# TODO: Locate shape centroid, find UTMs, and push values to BLM Proxy
