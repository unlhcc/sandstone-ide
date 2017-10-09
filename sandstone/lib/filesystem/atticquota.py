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
        # Percent full to show quota warning at.
        self.WARNING_PERCENT = 95
        # Time period prior to expiration to begin showing warning.
        self.EXPIRE_WINDOW = dt.timedelta(days=14)
        self.ALERTS = {
        'near_full' : { 'message' : """Your Attic quota is {0}% full!  Consider removing unneeded files to reduce usage.  Need more space?  Contact hcc-support@unl.edu to purchase additional storage.""", 
            'type': 'warning',
            'close': True },
        'full' :  { 'message':  """Your Attic space is full!  You won't be able to upload any more files until you reduce your usage.  Need more space?  Contact hcc-support@unl.edu to purchase additional storage.""",
            'type': 'warning',
            'close': True },
        'near_expire' : { 'message': """Your Attic space will expire soon!  Contact hcc-support@unl.edu to renew and retain access to your data.""",
            'type': 'warning',
            'close': True },
        'no_allocation' : { 'message': """Oops!  It looks like you haven't purchased Attic space, or it has been more than two weeks since your allocation expired.  See hcc.unl.edu/attic for details on reserving an allocation or contact hcc-support@unl.edu to renew.""",
            'type': 'danger',
            'close': False },
    }

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
             'expire_message' : friendly_expire_message,
             'expire_datetime' : expire_datetime.strftime('%Y-%m-%d %X'),
                }

        return (stats)

    def _add_alerts(self, volume_stats):
        """
        Add any needed alerts based on usage or expiration date.
        """
        alerts = []

        if (self.WARNING_PERCENT <= volume_stats['used_pct'] < 100):
            alerts.append({'message': self.ALERTS['near_full']['message'].format(volume_stats['used_pct']),
                'type': self.ALERTS['near_full']['type'], 'close': self.ALERTS['near_full']['close']})
        elif (volume_stats['used_pct'] == 100):
            alerts.append(self.ALERTS['full'])

        if (dt.datetime.strptime(volume_stats['expire_datetime'],'%Y-%m-%d %X') - dt.datetime.now() <= self.EXPIRE_WINDOW):
            alerts.append(self.ALERTS['near_expire'])

        return alerts

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
            alerts = []
            alerts.append(self.ALERTS['no_allocation'])
            return (attic_volume, alerts)

        (usage_stats) = self._parse_usage_file(usage_file_h)
        volume_stats.update(usage_stats)
        alerts = self._add_alerts(volume_stats)

        attic_volume = []
        attic_volume.append(VolumeObject(**volume_stats))
        return (attic_volume, alerts)
