.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _faq:

*******************
FAQ/Troubleshooting
*******************

If you encounter problems, you can always stop by `talk.vespene.io <http://talk.vespene.io>` to get help,
but try the following things first.

My build takes a long time to execute / hangs
---------------------------------------------

Vespne makes a lot of effort to try to ensure software checkouts are non-interactive.

Checkouts are always executed with timeout commands to not permanently block workers, but occasionally some
bad configurations may block builds for longer than you would like.

Your setup (per instructions) should first and foremost always execute workers with "ssh-agent".  If this is done,
SSH keys attached to the project will be used when checking out the project.

If the repo is not publically readable, check to make sure you have configured either a service login (for http or https URLs)
or an SSH key (for those that are not) on any project that is encountering problems.

If you provide a SSH key that is locked but it does not have a valid unlock password provided, the build will also take a while
before automatically failing. 

I see some error in the worker logs but don't have enough information
---------------------------------------------------------------------

The logs the worker normally outputs to standard out/error are consumed auotmatically by supervisord and stored in 
/var/log/vespene.  However, these logs are not neccessarily very verbose.

Build output is available by clicking on the build object in the web interface, or by looking at the physical log in
the build working directory.

When I click on the globe icon in the app to browse a build root, the URL is not valid or reachable
---------------------------------------------------------------------------------------------------

By default when running Vespene, workers check in and register their hostname in the database.  The purpose of this is so
that if there are multiple workers, those workers can serve their build roots automatically using the built-in Vespene
build server.

Of course, hostnames are notoriously unreliable.  If you find the hostnames are not what you would like, you can refer
to :ref:`settings` for information on setting the hostname in the worker configuration.

Alternatively, you could choose to use a post-build trigger (see :ref:`triggers`) to copy all build roots to a common location,
and then refer to :ref:`settings` to change the globe icon to point to that archive instead.  This would be the most reliable
option if you expect host names to change, for instance in a cloud context.

My build fails with a message about sudo
----------------------------------------

The default configuration for a worker pool uses "sudo" as the security isolation mechanism but does not provide
a username or password.

You'll need to fill one in.

For developer setups, if you are running Vespene under your user account, it's actually ok to just put the same
username down for the sudo user and leave the password blank.

Whatever user you select will need access to read the build-root.

My docker-isolated build can't take advantage of my SSH keys
------------------------------------------------------------

This is expected.  If you are using docker to isolate the security of builds on a given worker pool, SSH can be used
for checkout, but those same SSH keys are not available within the build environment, which actually happens inside
a docker build command.

For instance, if you are trying to deploy something with SSH, you need to switch to the "sudo" isolation type for
the worker pool.

If you want to still have container security isolation for other builds, create more than one worker pool, and just
use the sudo-isolated worker pool for your automation jobs.

Something isn't validated well in the GUI
-----------------------------------------

Vespene is still pretty new, so we don't do a lot of checking to see that you don't put in something like a limmerick
in the repo field of a project.  Rather, the system will wait until the build executes and may fail then.

Similarly, if you do something like put in invalid JSON in some places, the system may just fail a build with a traceback.

We'll improve most of these over time and these are on our short list to improve.

If you encounter some problem that was not easy to figure out, let us know. 

I am experiencing an error in the setup process
-----------------------------------------------

Sometimes distributions change or your local configurations will make our stock configurations not work well.

Try setting up Vespene on a clean machine and follow the instructions closely. 

This is definitely a good time to stop by the official forum.

If you are debugging a *development* setup, versus following the official installation steps, please share where
you hit a problem and what is unique about your environment.

Vespene doesn't live update with status
---------------------------------------

Currently Vespene does not contain any kind of web-socket implementation to do live updates of build status.

You'll just need to pretend it was 2005 and hit good-old-fashioned reload.

We also would like to make something a bit more friendly that would show a view on "/" with most recent builds
and attention to any failed builds, and make something more friendly for showing on a NOC.

Where is the REST API?
----------------------

A REST API for the system is not yet available, but will be added in late 2018.  This API may be read-only in first incantations.

Can I use Apache or NGINX with Vespene?
---------------------------------------

Yes, you can proxy Vespene's server (gnuicorn) with another web server.  However Vespene expects to be "/", so you can't mount
those URLs on a different URL space at this point.

How is Windows support?
-----------------------

I think this was mentinoed a few times in the docs, but we really haven't made any efforts to make this system support Windows yet.

However, most changes are related to paths and such, and if reasonably abstracted and clean, we're quite open to patches
that would add Windows support and would encourage them.

There are some obvious cases where we use shell tools in the build scripts (like "timeout") that may have to have conditional
behavior but we are not really using any Python modules that shouldn't be portable.

In short, it probably won't be terribly difficult.

Why is this UI forms based?
---------------------------

The UI is MUCH faster to develop this way, and more reliable, than if we had to track all the latest shiny things
in React or Angular development land.  We're quite open to CSS improvements now, but want to keep things simple in Javascript
land so it is easy to work on for everyone.

Right now, we only have a handful of templates and they are very generic for all object types.

What about Accessibility?
-------------------------

Sorry about that - this project is new, and it's quite obvious that things in the UI are *not* very accessible at this point. We're always open for tips, but I think the best way to handle this may be to make an EXCELLENT cli client that can do everything the UI can do.  This is also a good reason as it would provide a strong test layer for the proposed REST API. Such a CLI project would alos include an API library for easier access to the REST API.

This is on the radar, but it may happen after January 2019.

Does this project offer cowsay-integration?
-------------------------------------------

Thanks you for remembering past projects! It is time for new things, though.

What about Mobile?
------------------

I bet it looks pretty rough now!

While I've never wanted to look at build results on my phone, we're very open to mobile upgrades.
Stop by the forum and let's talk about how to do this.

Is your roadmap public?
-----------------------

We like to talk about good ideas all the time, but because a BETTER idea may come up tomorrow, we'd rather not release
a roadmap that would appear like any kind of commitment.  We'd also probably move way faster than that roadmap anyway.

Please join `talk.vespene.io <talk.vespene.io>` to talk about ideas!

I found a typo or grammar error in the docs
-------------------------------------------

Thank you!  We don't believe in automated spell check as it puts humans out of jobs.

More seriously, that's more because it's written in Sphinx and edited in vim. 
Documentation correction can be submitted by sending a pull request to the source code in docs/source.

What about X / Can We Improve X?
--------------------------------

Yes! The project is young and the sky is the limit, stop by the forum and let's talk about things!
No current design decisions, except those that will impact upgrades, are sacred at this point.

This includes openness to new types of plugins of all sorts.


