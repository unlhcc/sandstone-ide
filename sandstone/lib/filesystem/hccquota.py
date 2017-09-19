import pwd
import grp
import os
import re
import bitmath
import hccdu.rquota as rq
import hccdu.lquota as lq
from sandstone.lib.filesystem.schemas import VolumeObject

class HccQuota:
    """
    Get HCC quota information for home/work directories and
    returns a list of Sandstone volume objects.
    """

    def __init__(self):
        self.lustre_path = '/lustre'

    def _quota_to_volume_info(self, quota_stats, path='home'):
        """
        Converts HCC du quota information to a dictionary following the
        Sandstone Volume schema.
        """

        assert path in ('home', 'work'), "Invalid path '{0}'".format(path)

        # who are we
        pwe = pwd.getpwuid(os.getuid())

        volume = {}
        volume['type'] = 'volume'
        volume['username'] = pwe.pw_name
        volume['groupname'] = grp.getgrgid(pwe.pw_gid).gr_name

        # get user and primary group quota info
        user_quota_info = quota_stats[0]._asdict()
        primary_group_quota_info = quota_stats[1]._asdict()

        if path == 'home':
            # set the path to the home directory
            volume['filepath'] = pwe.pw_dir
            # add the user stats for /home
            volume.update(self._quota_to_stats(user_quota_info))
            # add the primary group stats for /home
            group_stats = self._add_group_stats(self._quota_to_stats(primary_group_quota_info))
            volume.update(group_stats)
            # for /home, use the user quota for % full
            volume['percent_full'] = volume['used_pct']
            return volume

        elif path == 'work':
            # set the path to the work directory
            volume['filepath'] = re.sub('^\/home','/work',pwe.pw_dir)
            # there's no user quota set on /work, so use the group one
            user_quota_info['dqb_bhardlimit'] = primary_group_quota_info['dqb_bhardlimit']
            volume.update(self._quota_to_stats(user_quota_info))
            group_stats = self._add_group_stats(self._quota_to_stats(primary_group_quota_info))
            volume.update(group_stats)
            # for /work, use the group quota for % full
            volume['percent_full'] = volume['group_used_pct']
            return volume


    def _quota_to_stats(self, q_obj):
        """
        Converts quota entry dict to stats dict.
        """

        used = bitmath.Byte(q_obj['dqb_curspace'])
        size = bitmath.KiB(q_obj['dqb_bhardlimit'])
        available = bitmath.Byte(size.bytes - used.bytes)
        used_pct = 100. * used.bytes/size.bytes

        stats = {
             'used' : used.best_prefix(system=bitmath.NIST).format("{value:.0f} {unit}"),
             'available' : available.best_prefix(system=bitmath.NIST).format("{value:.0f} {unit}"),
             'used_pct' : int('{:.0f}'.format(used_pct)),
             'size' : size.best_prefix(system=bitmath.NIST).format("{value:.0f} {unit}")
                }

        return stats


    def _add_group_stats(self, stats):
        """
        Adds group quota information to stats.
        """

        group_info = {
            'group_used' : stats['used'],
            'group_available' : stats['available'],
            'group_used_pct' : stats['used_pct'],
            'group_size' : stats['size'],
        }

        return group_info

    def get_hcc_volumes(self):
        """
        Returns a list of Sandstone volume objects for home/work directories.
        """

        hcc_volumes = []

        home_quota = rq.rquota_get(rq.rquota_find_home_mount())
        home_volume_stats = self._quota_to_volume_info(home_quota, path='home')
        home_volume = VolumeObject(**home_volume_stats)
        hcc_volumes.append(home_volume)

        work_quota = lq.lquota_get(self.lustre_path)
        work_volume_stats = self._quota_to_volume_info(work_quota, path='work')
        work_volume = VolumeObject(**work_volume_stats)
        hcc_volumes.append(work_volume)

        return hcc_volumes
