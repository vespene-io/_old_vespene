
.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _settings:

********
Settings
********

Day-to-day most configuration in Vespene (like defining new projects) will be done through the UI. Certain site-specific and admin-only behavior
is configured in settings files.

Because Vespene is a Django-based Python application, it uses a "settings.py" file that ships with the default Vespene
install, that includes numerous defaults.

To override the defaults, you can install a "local_settings.py" file (overriding any defaults you wish) in the same
directory as settings.py.

However, it is better to instead make any number of smaller python files in "/etc/vespene/settings.d".  For instance,
you could make a file "/etc/vespene/settings.d/my_settings.py".  Any file ending in ".py" will be loaded. 

There is a bit more discussion also in :ref:`plugins` and throughout the document, but below we have a list of all
user-configurable settings in alphabetical order. If a setting is in settings.py and is NOT addressed here, we don't
recommend you tweak it.

It is important that all Vespene instances (web nodes and workers) have a copy of the same settings.

ALLOWED_HOSTS
-------------

This is a Django setting that allows for what host names are valid origins for web requests.

If not set, access to the Vespene UI will be limited.

We recommend you create a file /etc/vespene/settings.d/allowed.py that sets something like this::

    ALLOWED_HOSTS = [
       '127.0.0.1',
       '.your-domain.com'
    ]

The default just allows everything in, and is only appropriate for internal access.  You should not put Vespene on a public
webserver anyway (see :ref:`security`).  That would look like this::

    ALLOWED_HOSTS = [ '*' ]

BUILDROOT_WEB_LINK
------------------

Vespene has one of two ways to serve up builds, as noted in :ref:`workers`. If you are using :ref:`triggers` to publish
builds to a particular common location, rather than desiring to serve files directly off the individual workers through the Python app, set the following
parameter and the Web UI will link to the common location instead of the in-built fileserving locations.

    BUILDROOT_WEB_LINK = "http://not-configured-by-your-vespene-admin-yet.example.com/builds/{{ build.id }}"

This could be an FTP URL, or even a smbfs network share.

DATABASE
--------

"DATABASE" contains the standard connection string information for Vespene.  Technically this would support anything that
Django supports but we only "support" PostgreSQL to keep development life simple.

If you follow the instructions in :ref:`setup`, you will get a file in /etc/vespene/settings.d that looks something like::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'vespene',
            'USER': 'vespene',
            'PASSWORD' : '$DBPASS',
            'HOST': '$DBSERVER',
            'ATOMIC_REQUESTS': True
        }
    }

The password and hostname should be replaced.  As noted in :ref:`security`, if using sudo isolation, the settings
file should not be readable by the sudo user, unless you want your builds to have database access. You don't.

BUILD_ROOT
----------

This setting chooses the temp directory each worker will use for builds. As mentioned elsewhere (see :ref:`triggers`),
this is usually not the directory final build results will go to, as frequently that would be on NFS or something similar.

This setting actually CAN be different between workers, and has no meaning if no workers are being run on a particular Vespene
node::

    BUILD_ROOT = "/tmp/vespene/buildroot/"

The usage of /tmp here is probably not appropriate and you should consider changing it.  When using sudo isolation, this directory
must be writeable by the configured sudo user, and in all cases should be writeable by the user who is running the Vespene worker
processes.

For buildroot management tips, see ref:`upkeep`.

FILESERVING_ENABLED
-------------------

If true, allows build results to be served up by the individual workers.  Access is annoymous and not hyper-efficient, if you want
something more robust you can use :ref:`triggers` to copy build results anywhere, then set BUILDROOT_WEB_LINK as above instead::

    FILESERVING_ENABLED = True

To access the fileserver and browse any build workspace within the app, click the globe icon beside any build.

FILESERVING_HOSTNAME
--------------------

Before each build, a worker will run the `hostname` command to find out what address it has.  This address is used to generate builds
so the interface can know how to link to various files.  Should the results of `hostname` be unreliable, you can set this parameter
in settings explicitly to just use a hard coded setting::

   FILESERVING_HOSTNAME = "worker1.example.com"

FILESERVING_PORT
----------------

The default fileserving port used is 8000, which may not be appropriate if you decided to proxy your Vespene configuration through
something like Apache or NGINX::

   FILESERVING_PORT = 8000

Otherwise, just leave it as is.

PLUGINS
-------

To avoid repetition, see :ref:`plugins` for more about plugin configuration.  There's a lot you can do.

TIME_DISPLAY_FORMAT
-------------------

For all those who would like to see their times displayed in different formats, this is for you.

The default is::

   TIME_DISPLAY_FORMAT = "%b %d %Y, %I:%M:%S %p"

This follows normal "strftime" conventions.


