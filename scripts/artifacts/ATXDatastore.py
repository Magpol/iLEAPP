# Module Description: Parses ATXDataStore and matches actions with Frequent locations, when availble.
# Author: @magpol
# Date: 2023-10-11
# Artifact version: 0.0.1
# Requirements: none

import re

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_atxDatastore(files_found, report_folder, seeker, wrap_text, timezone_offset):

# Matches items in _AtxDataStore to Frequent locations found in Locations.sqlite
    atxdb = ''
    localdb = ''
   
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('_ATXDataStore.db'):
           atxdb = str(file_found)

        if file_name.endswith('Local.sqlite'):
           localdb = str(file_found)
        else:
            continue
    
    db = open_sqlite_db_readonly(atxdb)
    cursor = db.cursor()

    cursor.execute('''attach database "''' + localdb + '''" as Local ''')
    cursor.execute('''select 
alog.id AS Id,
alog.bundleId AS bundleId,
alogAction.actionType as ptype,
Local.ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLATITUDE as latitude, 
Local.ZRTLEARNEDLOCATIONOFINTERESTMO.ZLOCATIONLONGITUDE as longitude,
DateTime(alog.date + 978307200, 'UNIXEPOCH', 'localtime') as date,
DateTime(alog.appSessionStartDate + 978307200, 'UNIXEPOCH', 'localtime') as appSessionStartDate,
DateTime(alog.appSessionEndDate + 978307200, 'UNIXEPOCH', 'localtime') as appSessionEndDate,
hex(alog.location) as location,
hex(alog.prevLocation) as prevLocation,
alog.motionType as potionType,
alog.geohash as geohash,
alog.coarseGeohash as coarseGeohash
FROM alog 
INNER JOIN alogAction on alogAction.id = alog.actionType
LEFT JOIN Local.ZRTLEARNEDLOCATIONOFINTERESTMO on Local.ZRTLEARNEDLOCATIONOFINTERESTMO.ZIDENTIFIER = alog.location
                            ''')

    all_rows = cursor.fetchall()

    if len(all_rows) > 0:
        
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[5], row[2],row[3],row[4],row[6],row[7],row[8],row[9]))

        report = ArtifactHtmlReport('ATXDataStore')
        report.start_artifact_report(report_folder, 'ATXDataStore')
        report.add_script()
        data_headers = ('ID', 'Date', 'Type', 'Lat', 'Long', 'AppSessionStartDate', 'AppSessionEndDate', 'Location', 'Previous Location')
        report.write_artifact_data_table(data_headers, data_list, atxdb)
        report.end_artifact_report()

        tsvname = 'ATXDataStore'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'ATXDataStore'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No items in ATXDataStore')

    db.close()
    return

__artifacts__ = {
    "ATXDatastore": (
        "iOS ATXDatastore",
        ('**DuetExpertCenter/_ATXDataStore.db*', '**routined/Local.sqlite*'),
        get_atxDatastore)
}
