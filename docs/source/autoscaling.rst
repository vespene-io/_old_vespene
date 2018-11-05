.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _autoscaling:

Autoscaling
===========

STATUS: New and Experimental!

In most use cases for Vespene, it's fine and perhaps easier to set up a fixed number of workers (see :ref:`worker_pools`).

If you expect build demand to be highly variable, however, you might want to change the number of workers automatically throughout
the day.

Even without using Vespene's built-in autoscaling, this could be done by manually adjusting an autoscaling group.

The Vespene autoscaler, however, is an advanced feature that dynamically adjusts the number of running workers in a Vespene worker
pool based on load.

It is a highly configurable system where both the "planner" and "executor" components are individually pluggable.

Worker Pool Configuration
-------------------------

To enable autoscaling, go to a worker pool in the UI, then go to the "Autoscaling Tab".  Check "enable autoscaling" and then
be prepared to feast on a slew of tuning options!

Select both a "planning" and "executor" plugin to implement your preferences. At this time, there's only one choice for both, so that is super easy.

The other options however require some explanation and are related to the mathematics behind the size calculations.

When the default 'stock' planner runs, it looks at the number of queued and running builds, and then executes a formula to determine
the desired number of workers to send to the executor plugin.

This formula is::

    b1 = (number_of_queued_builds * queued_weight) + (number_of_running_builds * running_weight)
    b2 = (b1 * multiplier) + excess
    result = min(max(b2, maximum), minimum)

The constants configured on the worker pool are as follows:

   * queued_weight - how many workers to allocate per queued build (default: 1)
   * running_weight - how many workers to allocate per running  build (default: 1)
   * multiplier - multiplies the calculated result by a floating point value (default: 1)
   * excess - a bonus number of builds to allocate regardless of the calculation (default: 0)
   * min (default: 0) and max (default: 10) - provide a bounds on the overall equation

The defaults should be good to use without modification in most cases.

In addition to the mentioned numbers, 'reevaluate_minutes' (default: 5) is used to recalculate the autoscaling dimensions after however many number of minutes.

This result is then fed into the executor step. 

Shell Executor
--------------

The shell executor runs the configured command with the following variables templated into it using the Jinja2 templating
language:

* worker - the worker pool object in Django
* size - the number of workers to allocate using the formula
* queued_size - the raw number of queued builds (subject to min and max) ignoring running builds

For example, if using Terraform, you might keep your terraform plans in a git repo.

The configured executor command might then be::

   (cd /opt/plans; git pull; terraform apply /opt/plans/{{ worker_pool.name }}.tf -var 'size={{ size}}')

If your provisioning system is declarative, always use the variable 'size' for the count.  

If you can't track the number of worker  instances once they are allocated, then you have a non-declarative system. In this case, deploy workloads only for 'queued_size' and then set 'reevaluate_minutes' to a large enough interval to avoid too much build churn.

Vespene cloud "Best Practices" would strongly encourage tagging all of your instances with "vespene_worker" and the name of the worker pool,
and this is something you can set up in your automation if applicable.

You don't have to use any specific tool with the executor, and can easily launch your own scripts.

Image Preparation
-----------------

If using the shell executor to deploy a cloud image it is VITAL to consider what must go
into the image to make for a successful build

When preparing a worker cloud image for autoscaling, make sure of the following:

   1. the image contains the same version of Vespene you are using for the web console
   2. the image contains a complete /etc/settings.d configuration as you would any other worker - especially secrets.py
   3. the image contains a configured build root in settings and this directory EXISTS
   4. the sudo user configured on the worker pool can write to the build root
   5. the image starts the worker pool script
   6. whatever environment the worker is deployed to has access to the Vespene database
   7. you are able to read the logs through use of some logfile aggregration service
   8. you are using triggers or a shared filesystem to access the build root after the builders terminate
   9. you don't start the web interface (there's no point to this, but won't hurt anything).
   10. be sure any build tools you need are baked in to avoid a lot of internet traffic fetching them

While having nothing to do with autoscaling, CI/CD ettiquette strongly encourages mirroring/caching any software dependencies
locally at your place of business. If running a lot of builds, you don't want to have build scripts that constantly 'wget' or 'curl' content or abusively re-download tools from online mirrors.

The Worker Command Line
-----------------------

Most importantly, the deployed image must start a worker.

In many cases, it is fine to launch a lightweight container or image that will start one build and then exit.

To do this, launch the worker as follows::

   ssh-agent <path-to-python3> manage.py worker <worker-pool-name> --max-builds=1 --max-wait-minutes=5

To deploy a worker that runs a finite number of builds and then exits do something like this::
   
   ssh-agent <path-to-python3> manage.py worker <worker-pool-name> --max-builds=10 --max-wait-minutes=60

If your invocation does not have 'declarativeness' and is strictly going to allocate new workers without checking
to see how many new workers to allocate, it is very important to not forget '--max-builds=1'. In this scenario
you could rapidly consume a very large amount of cloud resources!

It is possible that your automation script downsizing build capacity could terminate some running builds.
If this is a concern, your cloud provider may provide some solutions such as `AWS Autoscaling Delay Termination <https://aws.amazon.com/premiumsupport/knowledge-center/auto-scaling-delay-termination/>`_. In doing this, set the termination time to something like one hour, and also consider
setting your termination policy to always terminate the oldest instances.

Multiple Workers Per Instance
-----------------------------

Most users will not want multiple workers per instance.

If you are asking for a particularly large instance with this autoscaling feature, you can run multiple workers per instance.

Instead of directly launching the worker script like so::

   ssh-agent <path-to-python3> manage.py worker <worker-pool-name> --max-builds=1 --max-wait-minutes=5

You would instead use a tool like supervisor to launch multiple copies of the same worker script, still with the same parameters.

Suppose you wanted to run four worker processes per instance.  In this situation, have the image launch the four worker processes,
but change the multiplier in the worker pool configuration to 4.

Make sure that supervisor is not set to restart the workers when they terminate, and when all four instances are down,
supervisor itself should stop.

Running the Autoscaling Engine
------------------------------

A management process is required to monitor the worker pools and send off autoscaling requests.  This process should have access to any
cloud commands you need to run::

   python manage.py autoscaler --queue <worker-pool-name> --queue <worker-pool_name>

Any plugins need to be abled in :ref:`settings` and selected on the individual worker pools.

To disable autoscaling for any worker, just hop over to the worker pool tab in the UI and uncheck the feature.

This autoscaler process only needs to have one copy running per worker pool, and one process can easily oversee all of your
worker pools if you want.  Executors *will* block until complete though, so if you want the highest levels of parallelism, consider
starting one seperate autoscaler for each worker pool::

   python manage.py autoscaler --queue <worker-pool-name1>
   python manage.py autoscaler --queue <worker-pool-name2>

The tools log to standard output, so consider adding them to your supervisor configuration and redirecting the output to /var/log/vespene/
if you wish. The autoscaler process is NOT set up by default in the stock Vespene setup scripts.

If you need to run the autoscaling engine *now*, the force flag is helpful::

   python manage.py autoscaler --queue <worker-pool-name1> --force

The force flag will ignore any timing restrictions, run the scaling loop once, and then immediately exit.

Additionally, there is a "--sleep" flag that takes an integer.  This is used to calculate how long to sleep between
each calculation loop.  The default is 20 seconds.  The only point in this value is to avoid hammering the database.
It has no meaning with --force.

Debugging
---------

Ephemeral workers will naturally be harder to debug than machines you can simply log into and explore.

Making sure logs to /var/log/vespene (or standard out, as appropriate) are centralized will be important to
understanding any errors in autoscaling. If you aren't starting worker through supervisor, you're not going to have
/var/log/vespene by default and will have to log output on your own.  Redirecting to /var/log/vespene is reasonable.

Once again, be sure triggers are configured to copy build roots once completed to a common location, or that a 
shared filesystem is in use.

Conclusion
----------

We hope you find the autoscaling engine to be very flexible and very pluggable.

If you are just getting Vespene started and learning how to use it, we first recommend you learn Vespene and make sure it is a tool for you, and that
you are familiar with concepts. Try this feature *after* you are familiar with the basics and you should get along fine.  

This feature is also very new in Vespene, so please stop by talk.vespene.io with any ideas, questions, or feedback!


