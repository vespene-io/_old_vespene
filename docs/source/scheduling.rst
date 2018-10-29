.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _scheduling:

Scheduling
----------

Vespene can be configured to run jobs on a periodic basis.

To enable this feature, go to the "Scheduling" tab when editing a project.

First, enable the "scheduling_enabled" checkbox, which is off by default.

Afterwards, select what days the schedule will apply.

Once the days are selected, you can now configure exactly what hour and minute combinations where a job will be queued up.

This hour and minute combination setting is different for weekends and weekdays, allowing for optionally running a job
less frequently on a weekend.

It's not a fully flexible calendar system, because we just wanted to keep it fairly straightforward, but is possibly
a good balance between something like cron and something more like repeating calendar invites.

Example
=======

To run a job every weekday at noon and 5pm Eastern time.
Go into the "schedule" tab for a project.

Check "schedule_enable"

Check "monday", "tuesday", "wednesday", "thursday", and "friday"

In the "weekday_start_hours" field enter "16, 19". 16 and 19 are the UTC hours for Noon and 5PM eastern.

In the "weekday_start_minutes" field enter "0".  This means to queue a job at exactly noon and 5pm.

When Do Jobs Start
==================

This system requires builders to build jobs, and it is quite possible that a builder will be busy and not
start a job immediately.

What will happen is that when a builder has time, it will consult the project configurations and queue up new
jobs according to the schedule.

When the workers reach for a new job to run, it may be one of the jobs that are queued up from the scheduler.
If not, the job will run when it can.

If you would like scheduled jobs to run promptly, consider allocating extra workers to the worker pool.

The setting "schedule_threshold" in project settings is there as a safeguard against extraneous scheduling.  For instance,
if you want to run a project every 30 minutes, but a build occured 10 minutes ago triggered by a pipeline that was ultimately triggered
by a CI/CD webhook, you might not need to run a new build.  The default schedule_threshold is 10 minutes.  We don't recommend
reducing it, but you may want to increase it to thirty (30) minutes or so to prevent infrastructure churn in some scenarios.

Scheduler Considerations
========================

There needs to be at least one worker process running for jobs to get scheduled.

If you would like
to disable a scheduler during an outage window, you can uncheck the "schedule_enabled" checkbox and still leave all of the 
other scheduler settings saved in the database for when you re-enable it later. 

Scheduled jobs are kicked off by the backend and will intentionally ignore answering :ref:`launch_questions` that are set.
If your project uses launch questions the template should have defaults, which are probably most easily set with the Jinja2 "| default" filter.

Job scheduling logic, like all mogwai, may have some unexpected behavior around UTC midnight. Also, do not get the job scheduler wet.
 

