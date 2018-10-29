.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _plugins:

Plugins
=======

Vespene is highly pluggable. 

Plugins can be loaded from anywhere in the PYTHON_PATH and are configured in settings files, such as /etc/vespene/settings.d/plugins.py.

Contribution of new plugins is very welcome!  We'd much rather maintain a plugin we could all share than
have folks try to hunt down plugins.  See :ref:`resources` for details on how to contribute.

The Plugin Configuration
------------------------

While it can be overridden in /etc/vespene/settings.d/ or vespene/local_settings.py, the stock plugin configuration
that ships with Vespene is as follows::

    PLUGIN_CONFIGURATION = dict(
        pre_triggers = OrderedDict(
            # slack_general = [ "vespene.plugins.triggers.slack", dict(channel='general', token=SLACK_TOKEN) ]
        ),
        success_triggers = OrderedDict(
            # slack_general = [ "vespene.plugins.triggers.slack", dict(channel='general', token=SLACK_TOKEN) ],
            # publish = [ "vespene.plugins.triggers.command", "echo cp - a {{ build.working_dir }} /tmp/publish_dir" ] 
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
        output = OrderedDict(
            timestamp = [ "vespene.plugins.output.timestamp", dict(mode='elapsed') ]
        ),
        authorization = OrderedDict(
            ownership = [ "vespene.plugins.authorization.ownership", {} ],
            group_required = [ "vespene.plugins.authorization.group_required", {} ]
        ),
        organizations = OrderedDict(
            github = "vespene.plugins.importing.github"
        ),
        variables = OrderedDict(
            common = "vespene.plugins.variables.common",
            pipelines = "vespene.plugins.variables.pipelines",
            snippets = "vespene.plugins.variables.snippets"
        )
    )


You can use this configuration for reference when reading the rest of this chapter.

The commented out lines are just examples because we expect build triggers are things many people will want to configure.

Adding plugins is almost always ok.  Most just add new behaviors.

There are some plugins that you shouldn't remove too casually though - access control policy is relatively important, and if you
are using git, you'll want git support for SCM checkouts.  See :ref:`authz` for details.

.. _triggers:

Trigger Plugins
---------------

Vespene ships with two triggers, one that runs arbitrary commands, and another that sends slack notifications.

Triggers are probably the most common type of plugin people are going to write.  If you come up with something cool, we would
love a contribution to the codebase to add it.

For many extensions though, you can just rely on the "command" trigger and call shell commands - that may be easiest, especially
for those who don't want to write any python code.

Triggers are run before or after builds, and triggers can be configured seperately for success or failure scenarios.

Multiple copies of the same trigger can be used with different parameters, they just have to be given different names.

Trigger Plugins: Command
------------------------

The command plugin can run any shell command, but before it does, the command string is templated with data about the build
and project, using Jinja2.  
            
For instance, to copy successful builds to NFS, the following might be configured as a success_trigger:

    publish = [ "vespene.plugins.triggers.command", "echo cp - a {{ build.working_dir }} /tmp/publish_dir" ] 

Other uses from copying might be to call a notification script written in another programming language.

Variables like "{{ build.id }}" and "{{ project.name }}" might be useful parameters.

The program executed should be marked executable and can signal a failure with a non-zero exit status.

Trigger Plugins: Slack Plugin
-----------------------------

The slack plugin is invoked as follows:

    slack_general = [ "vespene.plugins.triggers.slack", dict(channel='general', token=SLACK_TOKEN) ]

It takes the channel name and a long-form slack OAUTH token as a parameter.  It's a little rough and improvements to it are quite welcome,
as are additions of other chat services other than Slack (such as IRC, Rocket Chat, Hipchat, etc).

Output Plugins
--------------

Output plugins take the output of a build line (or an internal message about build housekeeping, like SCM checkouts) and process them.

The default output plugin 'timestamp' adds a timestamp to each line in the build output.

Plugins don't have to just filter the output, they could, for example, send output to an additional logfile or logging service, or even
play sound effects when they see certain build messages.  It's really up to you.

The sound effects idea may annoy coworkers.

SCM Plugins
-----------

All source control types (such as git) supported in Vespene are implemented as plugins.

When writing a new plugin, make sure the following cases are handled:

* Checkouts of public content
* Support for naming a branch to check out.
* Checkouts of private content, using SSH keys and passwords stored in Vespene
* Recording the lastest revision at checkout time.
* Checking out only the specified branch.
* Recording the user who made the last repository change on the branch.

We ship with git and svn (Subversion) plugins but really you could make source code come from any kind of system.
Technically, a SCM plugin could lie and extract something from an s3 bucket as long as the plugin implemented
the right methods!

SCM: git
--------

The git plugin is fully featured, and supports using SSH keys attached to the project, as well as username/passwords set in Service Login objects
attached to the project. 

SCM: svn
--------

The SVN (Subversion) plugin is emergent and possibly could use some upgrades, as we are not heavy users of SVN.  It supports anonymous SVN and also username
and password authentication.  

SCM: none
---------

The none plugin is just a placeholder and indicates there is no checkout needed and the project is just a generic build script.  This same
behavior occurs if a real SCM type is selected and the repository value is left blank.

SCM: future
-----------

We're quite interested in support for nearly all SCM types. See :ref:`resources` for ways to contribute.

Isolation Plugins
-----------------

Isolation modes, like sudo and docker containerization during the build process are also pluggable.  They are designed to protect builds from polluting the environment of one another,
or affecting the worker OS itself.

We ship with support for containers (via docker) and sudo, but this would be easily extensible to support chroots or jails, or maybe even an on-demand scheduler that spins up build
resources.

Contributions for these would be very welcome.

Isolation: basic_container
--------------------------

This plugin uses docker commands to isolate the build process that occurs after performing a checkout.  First, a base image of the selected type is crafted.  If special authentication is needed to pull
the base image, set this up in advance.  The build script is then run inside a "docker build" command, with the build root copied into the image.  The build root is then extracted *from* the image, and
the system cleans up all the intermediate work.  The intended goal here is running the build, not producing a container.

This build isolation method is preferred over sudo for security reasons, but has the slight operational downside of not being able to see intermediate build output until the build process is complete.
This limitation might be removable with some code modifications and is something we'd like to explore.

Isolation: sudo
---------------

This plugin sudoes to the configured sudo user after jumping into the build root.

It is very important (see :ref:`security`)) that if using this isolation mode the specified sudo user can not read the database settings for the Vespene application.  It is also possible
for build scripts in this build mode to read and write the contents of other build roots.

Isolation: future
-----------------

We're quite interested in contributions to other types of plugins, such as chroot, jails, alternative container implementations, LXC, cgroups, etc.  Contributions are very welcome!

Authentication Plugins
----------------------

It's a trap!  This is not actually handled by a Vespene plugin, but by Djagno middleware set
in settings.py.  You can still change the auth middleware to something else you write, but we
didn't have to build this into Vespene because it was already in Django.

We are quite interested in documentation, however, on setting up LDAP and SSO solutions like Okta.
This might involve a future plugin type or just Django middleware.

Django middleware should basically create a real database user for any user who logs in, because the various
models take advantage of that user.

Authorization Plugins
---------------------

How Vespene decides who can access what is also a plugin, allowing admins to replace the business logic
easily, if desired.

All authorization plugins are run that are configured in settings - if checks pass for one plugin, they must pass
for the rest of them before access to do something is granted.

Because authorization policy is somewhat involved, discussion of this plugin has been moved to a seperate
documentation page, see :ref:`authz`.

UI: Future
----------

Right now plugins can't present their own UI configuration panels or have their own storage in the database.  I somewhat want to go slow
on this having seen what this does to some other CI tools in terms of usability, but I suspect it will happen in the future. There wouldn't
be UI specific plugin types but it is possible a plugin might be able to declare a UI control panel for a particular object type and have
access to a JSON storage table.

Organization (Importing) Plugins
--------------------------------

Vespene can auto-import definitions (and scripts! and configurations!) directly from your source control organizations and save
a large amount of UI configuration.  See :ref:`importing` for details.

Variable Plugins
----------------

As shown in the default settings.py, variables control the order of operations for evaluating the variables that finally result in
vespene.json in a buildroot, and the context of template evaluation that results in a final build script, as per :ref:`variables`.

Most users should not rearrange these because it would be confusing to users of other Vespene environments (and readers of the
documentation), but you can.

You could also modify this to pull in variables from an arbitrary key-value store or pretty much anything you want.

Developing Plugins
------------------

To learn how to develop plugins, see :ref:`development_guide`.  

Other Plugin Types
------------------

If you think some other behavior types should be pluggable, we're very interested in hearing those ideas too! Stop by the forum!
