.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _cli:

CLI
===

Vespene has a few CLI commands available in addition to the web interface.

These are "standard" "manage.py" Django management commands, which are easiest to execute by SSH'ing into a Vespene node.
Django management commands provide an easy way to interface with the database without running through the whole web stack.

Custom commands that ship with Vespene include:

Job Execution
-------------

Jobs may be manually started/stopped from the command line as follows:

    python manage.py job_control --project <project-id> [--start|--stop]

This may be extended to support project names and other options in the future.

Tutorial setup
--------------

As described in [the Tutorial](tutorial.html), this creates several objects for a basic demo:

   python manage.py tutorial_setup

Cleanup
-------

To clean up old build roots on a worker, older than a certain number of days, run this on each worker:

   python manage.py cleanup --remove-build-roots --days=30

To clean up builds older than a certain number of days, run this on any node with database access:

   python manage.py cleanup --remove-builds --days=30

The state of the build is not considered, only the age based on the time when the build was first queued.

Stale queued builds (such as ones that were never started) are automatically cleaned up by the worker processes with no
commands required to manage them.

This would be a good command to consider adding to a crontab.

Future
------

More commands will be added over time. If you have an idea for a useful command to contribute see :ref:`resources`.





