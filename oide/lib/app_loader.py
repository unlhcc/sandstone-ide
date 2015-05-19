import logging
import oide.settings as global_settings



def get_installed_app_static_specs():
    spec_list = []
    for app_name in global_settings.INSTALLED_APPS:
        try:
            app_settings = __import__(app_name+'.settings',fromlist=[''])
            spec_list.append(
                (
                    app_settings.APP_SPECIFICATION['NG_MODULE_NAME'],
                    app_settings.APP_DIRECTORY
                )
            )
        except ImportError:
            logging.debug('No settings specified for app: %s'%app_name)
        except AttributeError:
            logging.debug('No app spec or directory specified for app: %s'%app_name)
    return spec_list

def get_installed_app_specs():
    spec_list = []
    for app_name in global_settings.INSTALLED_APPS:
        try:
            app_settings = __import__(app_name+'.settings',fromlist=[''])
            spec_list.append(app_settings.APP_SPECIFICATION)
        except ImportError:
            logging.debug('No settings specified for app: %s'%app_name)
        except AttributeError:
            logging.debug('No app spec for app: %s'%app_name)
    return spec_list

def get_installed_app_cmds():
    cmd_list = []
    for app_name in global_settings.INSTALLED_APPS:
        try:
            app_settings = __import__(app_name+'.settings',fromlist=[''])
            cmd_list += list(app_settings.POST_AUTH_COMMANDS)
        except ImportError:
            logging.debug('No settings specified for app: %s'%app_name)
        except AttributeError:
            logging.debug('No post-auth commands for app: %s'%app_name)
    return cmd_list
