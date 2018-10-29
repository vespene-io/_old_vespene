.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _development_guide:

Development Guide
=================

If you are interested in developing on Vespene, excellent!

Maybe you just want to add a bug, or perhaps you want to add a plugin.  If you'd like to share code back with us, that's encouraged, but not required.
In this chapter, we'll go over a little of everything.

If you are thinking about adding something new, see :ref:`resources` for information about the discussion forum. Talking about ideas up front may
reduce duplicate efforts.

Architecture
------------

There are two tiers to the application, technically - the web node and workers, but realistically every machine in a cluster is going to run the web node, and it is the number of workers that vary. Web nodes can run worker processes too, of course.

The web app uses Django (via Python 3) and talks to the PostgreSQL database. Workers use Django model code (but no web stack) and share the same database.  Both are kicked off by supervisord, which in the production setup, is in turn launched by systemd (or whatever is the init system for the OS).

Code Structure
--------------

Inside the main checkout there are several directories, the main one 'vespene' has some important subdirectories to understand:

* common - code used by both the worker and web frontend (aka "manager")
* config - default settings to be used when there are no overriding settings in /etc/vespene/settings.d
* jinja2 - templates used by the frontend
* management - this is a django-standard directory for extensions to the 'manage.py' command line
* manager - code that is specific to the web frontend and that does not run on the workers.
* models - all ORM models with associated business logic
* plugins - see :ref: `plugins`, these may be executed by the manager or worker depending on the type of plugin
* static - random assets such as javascript support libraries and graphics. 
* views - code supporting the manager web UI. Business logic should go in 'model' objects or 'manager' instead (also plugins).
* workers - logic that workers run to actually execute the builds. Can call into plugins, model, and common code.

There are also some top level files:

* admin.py - entry point for the /admin Django admin interface
* settings.py - entry point for settings, but mostly stored in config/
* wsgi.py - entry point for gunicorn, our webserver

Code Conventions
----------------

A few small rules:

* Mostly, code for maintaince so that the largest number of people possibly can understand it
* Four space indent in Python is expected
* PEP8 limits readability (whoa, controversy!), please do not submit PEP8 or whitespace corrections (sorry!) as these break attribution tracking (aka "git blame").
* Make sure python source files have the same license header as the other python files
* Explain all files at the top of the files
* Make decent use of docstring comments throughout files
* Javascript should avoid using clippy.js - in general, limit javascript, we don't want to require people to know a lot of it.

Javascript & Static File Changes
--------------------------------

* application specific javascript is in vespene.js - there isn't a lot
* Right now there is a very small amount of javascript because the UI is still form based. This may not stay that way but was good for a start.
* Be sure to run "python manage.py collectstatic" or changes you make in your editor won't be served up by Django
* All dependencies must be vendored - we want to enable Vespene to work on closed networks - so no CDNs.
* We may have this minified better in the future.

Database Changes
----------------

We must always think of existing users when making model changes, and be very careful when proposing model changes:

* "make migrations" must be run after making any database ORM changes, add any new files in "migrations/" to git with "git add <filename>" before sending a PR that adds a field.
* Pay attention to any searches the application will use and add appropriate indexes in models.py when adding new fields when tables are going to be large
* Minimize database migrations through list discussion, only one migration is allowed per feature, and we like to plan ahead and group them together as we can not easily consolidate them.
* When adding fields to models, be sure to update forms.py 
* When adding new object types, add to models/, but also don't forget the UI - views/, templates/theme.j2, and forms.py

Adding Plugins
--------------

Look at the existing 'plugins/' folder and read :ref:`plugins` for how they work.  

To make a new plugin each class must be named Plugin. Nothing expensive (such as a network request) should be done in the constructor as the plugin may be instantiated quite frequently.

Plugins should be coded to be resilient to error and use meaningful logs and exceptions.

Plugins technically can call other plugins, but avoid doing so, as it might make the code confusing to trace.

Change settings.py to include the plugin if it is to be included by default, but likely we'll need to describe the plugin on the plugins page either way if submitting it for inclusion in the main distribution. This is probably a discussion to be had on the pull request.

If in doubt ask questions on the `forum <https://talk.vespene.io>`_, we'd be happy to help.

Dynamic Imports
---------------

If a plugin uses a library that not all users will be using, it can be dynamically imported like so::

    HAS_FOOLIB = False
    try:
        import some_dependency
        HAS_FOOLIB = True
    except ImportError:
        pass

And in the code for the plugin::

    if not HAS_FOOLIB:
       raise Exception("missing dependency: pip install foolib")

For instance, we would probably include a depdency for Slack or Hipchat, but would be unlikely to include
a dependency for a lesser used feature like Jabber.


Debugging Tips
--------------

This is all pretty standard web stack stuff, but mostly it helps to make sure you are seeing all the program output.

It's easiest if you run the webserver from "make run" and the worker from commands like "ssh-agent manage.py worker <queue-name>" so you can see
standard output.

If you run things through the stock supervisor configuration, standard output will get sent to /var/log/vespene. Alternatively, you could
reconfigure supervisor.

Sorry, there are no major debugger tips here, but whatever you are used to will work fine.



