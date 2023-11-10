from transkoder import Transkoder, print_result

# Initiate connection and fetch project names
transkoders = Transkoder()

# Print project names
# print('Project Names')
# print_result(transkoders.projects, ' ')

# Print all setting names w/ category & types
# print('Settings')
# print_result(transkoders.list_settings(True), " ")

# Example: Set "PlaybackGroup" for all projects in database
# transkoders.set_setting('PlaybackGroup', '1')

# Example: Get "PlaybackGroup" for all projects in database
# print('PlaybackGroup:')
# print_result(transkoders.get_setting("PlaybackGroup"), "  ")

# Example: Batch execute any SQL statement (This will list file names of all media in project)
# print_result(transkoders.execute_all_servers('SELECT value FROM mediametadata WHERE name = %s', ['FileName']))

# Example: Delete custom mixdowns for all projects in database
# transkoders.delete_setting("Mixdown019")
# transkoders.delete_setting("Mixdown019_mixdown")
# transkoders.delete_setting("Mixdown020")
# transkoders.delete_setting("Mixdown020_mixdown")
# transkoders.delete_setting("Mixdown021")
# transkoders.delete_setting("Mixdown021_mixdown")
# print("Custom mixdowns removed from all projects")

# Example: Copy specific settings from a given project to all projects
# server_proj = (1, "Chapeaux_S1_Ep1_Texted_TIFF")
# copy_settings = ["Mixdown001", "Mixdown001_mixdown", "Mixdown002", "Mixdown002_mixdown"]
# setting_data = transkoders.list_settings(True, *server_proj)
#
# for setting in copy_settings:
#     data = setting_data[setting]
#     data["setting"] = setting
#     data["value"] = transkoders.get_setting(setting, *server_proj)[0][0]
#     transkoders.upsert_setting(**data)
