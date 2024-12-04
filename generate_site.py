import os
import electric_toolbox
WEBSITE_DIRECTORY = "website"

os.mkdir(WEBSITE_DIRECTORY)

electric_toolbox.build_index(path=WEBSITE_DIRECTORY)