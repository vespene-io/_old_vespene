#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
# ---------------------------------------------------------------------------
# plugins.py - default plugin configuration - see web docs on plugins
# ---------------------------------------------------------------------------

from collections import OrderedDict

PLUGIN_SEARCH_PATH = [ ]

# used only by the slack plugin 
SLACK_CHANNEL = "general"
SLACK_TOKEN = "REPLACE-WITH-OAUTH-KEY"

PLUGIN_CONFIGURATION = dict(

    pre_triggers = OrderedDict(
        # slack_general = [ "vespene.plugins.triggers.slack", dict(channel='general', token=SLACK_TOKEN) ]
    ),

    # it is recommended that you enable publishing triggers to copy temporary buildroots to some location
    # pointed at by the BUILDROOT_WEB_LINK setting if you wish to browse buildroots in the web interface.
    # if you want to DISABLE this and do not include any publishing triggers, also set BUILDROOT_WEB_LINK
    # to an empty string elsewhere in settings.

    success_triggers = OrderedDict(
        # publish = [ "vespene.plugins.triggers.command", "cp -a {{ build.working_dir }} /tmp/publish_dir" ], 
        # slack_general = [ "vespene.plugins.triggers.slack", dict(channel='general', token=SLACK_TOKEN) ]
    ),
    failure_triggers = OrderedDict(
        # slack_general = [ "vespene.plugins.triggers.slack", dict(channel='general', token=SLACK_TOKEN) ]
    ),

    scm = OrderedDict(
        none = "vespene.plugins.scm.none",
        git = "vespene.plugins.scm.git",
        svn = "vespene.plugins.scm.svn"
    ), 

    isolation = OrderedDict(
        sudo = "vespene.plugins.isolation.sudo",
        basic_container = "vespene.plugins.isolation.basic_container"
    ),
    
    authorization = OrderedDict(
        ownership = [ "vespene.plugins.authorization.ownership", dict(filter_view=True) ],
        # additional  requirements beyond the ownership plugin:
        group_required = [ "vespene.plugins.authorization.group_required", dict(
                project = dict(
                    # create = [ 'developers', 'qa', 'ops'],
                )
            )
        ]
    ),

    output = OrderedDict(
        timestamp = [ "vespene.plugins.output.timestamp", dict(mode='elapsed') ]
    ),

    # with the secrets configuration, all loaded configurations can be read, but only the first will be used
    # for cloaking new secrets

    secrets = OrderedDict(
        basic     = "vespene.plugins.secrets.basic"
    ),

    organizations = OrderedDict(
        github = "vespene.plugins.organizations.github"
    ),
    
    # variable settings warning: changing these will probably confuse anyone you are discussing this with on the Vespene
    # forum, so if you tweak this, explain this going in to any discussion about variables!

    variables = OrderedDict(
        common = "vespene.plugins.variables.common",
        pipelines = "vespene.plugins.variables.pipelines",
        snippets = "vespene.plugins.variables.snippets"
    ),

    # autoscaling

    autoscaling_executors = OrderedDict(
        shell = "vespene.plugins.autoscale_executor.shell"
    ),
    autoscaling_planners = OrderedDict(
        stock = "vespene.plugins.autoscale_planner.stock",
    )
)
