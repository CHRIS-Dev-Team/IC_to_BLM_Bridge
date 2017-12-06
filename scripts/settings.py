import tkFileDialog
import json


icdb = ''
gis_db = ''
proxy_db = ''
project_boundaries = ''
mxd = ''


def load_settings():
    with open('settings.json') as settings_file:
        data = json.load(settings_file)
        global icdb, gis_db, proxy_db, mxd, project_boundaries
        icdb = data['icdb_backend']
        gis_db = data['gis_db']
        proxy_db = data['BLM_proxy_db']
        mxd = data['mxd']
        project_boundaries = data["project_boundaries"]
        return data


def update_settings(key, value):
    with open('settings.json','w') as settings_file:
        for parameter in settings:
            if key == parameter:
                settings[key] = value
        print settings
        json.dump(settings, settings_file, indent=4, separators=(',', ': '))


def setup():
        icdb_loc = tkFileDialog.askopenfilename()
        update_settings('icdb_backend', icdb_loc)
        gis_loc = tkFileDialog.askopenfilename()
        update_settings('gis_db', gis_loc)
        blm_loc = tkFileDialog.askdirectory()
        update_settings('BLM_proxy_db', blm_loc)
        mxd_loc = tkFileDialog.askopenfilename()
        update_settings('mxd', mxd_loc)
        proj_bound_loc = tkFileDialog.askopenfilename()
        update_settings('project_boundaries', proj_bound_loc)

settings = load_settings()
if settings["initial_run"] is False:
    settings["initial_run"] = True
    setup()
    load_settings()

