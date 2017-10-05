import os
import re
import datetime as dt
import pwd
import bitmath
from sandstone.lib.filesystem.schemas import VolumeObject

class AtticQuota:
    """
    Get Attic usage, expiration information.
    """

    def __init__(self):
        self.usage_file = 'disk_usage.txt'

    def _parse_usage_file(self, usage_file_handle):
        """
        Parse the usage file and return a dict of properties.
        """
        (header,space,expire) = usage_file_handle.readlines()

        # Determine usage
        (space_size, space_used) = space.strip().split()
        size = bitmath.parse_string_unsafe(space_size)
        used = bitmath.parse_string_unsafe(space_used)
        available = bitmath.Byte(size.bytes - used.bytes)
        used_pct = 100. * used.bytes/size.bytes

        # Get the time and date of expiration, and reformat in a friendly datetime format.
        (expire_date, expire_time) = expire.strip().split()[-2:]
        expire_datetime = dt.datetime.strptime('{} {}'.format(expire_date,expire_time), '%Y-%m-%d %X')
        friendly_expire_message = ' '.join(expire.split()[0:5] + [expire_datetime.strftime("%B %d, %Y at %I:%M:%S %p")])

        stats = {
             'used' : used.best_prefix(system=bitmath.SI).format("{value:.0f} {unit}"),
             'available' : available.best_prefix(system=bitmath.SI).format("{value:.0f} {unit}") if available.value else '0',
             'used_pct' : int('{:.0f}'.format(used_pct)),
             'size' : size.best_prefix(system=bitmath.SI).format("{value:.0f} {unit}"),
             'expire_message' : friendly_expire_message
                }

        return (stats)

    def get_attic_volume(self):
        """
        Get Attic usage information.
        """
        # who are we
        pwe = pwd.getpwuid(os.getuid())

        volume_stats = {}
        volume_stats['type'] = 'volume'

        # set the path to the Attic directory
        attic_dir = re.sub('^\/home','/attic',pwe.pw_dir)
        volume_stats['filepath'] = attic_dir
        # set the path to the usage file
        usage_file = os.path.join(os.path.split(attic_dir)[0],self.usage_file)

        # Try to open the usage file.
        try:
            usage_file_h = open(usage_file,'r')
        except IOError:
            # File can't be opened.  Either the user never had an allocation,
            # or it's been > 2 weeks since it expired.  Return an empty list.
            attic_volume = []
            alert = "No valid allocation"
            return (attic_volume, alert)

        (usage_stats) = self._parse_usage_file(usage_file_h)
        volume_stats.update(usage_stats)
        attic_volume = []
        attic_volume.append(VolumeObject(**volume_stats))
        alert = None
        return (attic_volume, alert)
