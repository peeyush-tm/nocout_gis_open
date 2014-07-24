"""Apache page handler for nocout_gis Device App web-services
"""

import nocout
import nocout_live

pagehandlers.update({
    "nocout": nocout.main,
    "nocout_live": nocout_live.main
})
