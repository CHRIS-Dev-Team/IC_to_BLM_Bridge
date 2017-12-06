from scripts import settings
from scripts.transfer_tool import ToProxy
from scripts.errors import get_log_path

print "--------\n" \
      "Welcome to the IC to BLM conversion tool.\n\n" \
      "If this is your first time running the program you \n" \
      "will be prompted to locate the ICDB backend database, \n" \
      "GIS backend database, and the proxy database.\n" \
      "--------\n"

program_pause = raw_input("Press enter to continue.")

log = open(get_log_path(), "w")
x = ToProxy(settings.gis_db, settings.proxy_db, settings.project_boundaries, log)
# x.send_resources_to_proxy("1 Meter")
x.send_reports_to_proxy("1 Meter")
log.close()
