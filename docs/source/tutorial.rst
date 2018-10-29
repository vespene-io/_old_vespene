.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _tutorial:

Tutorial
========

Welcome to the tutorial! We are glad to have you here!

We assume you have already ran the :ref:`setup` instructions and have a Vespene instance ready? If not, please
make sure that is done first and then come back here.

Ok? Good to go? Let's start learning Vespene!

Initialization
--------------

As per the :ref:`setup`, you should have already run this once::

   python manage.py tutorial_setup.

This populates Vespene with some sample builds - they don't do very much, and a basic configuration, to make it a bit more friendly when logging in
for the first time.

Should you ever delete the tutorial objects, you can re-run this command at any time to restore them.

Logging In
----------

Visit the homepage and type in your username and password for the superuser account to login::

	http://servername.example.com/

Once you see the login page, enter your username and password, and you'll be taken to the "Projects" screen,
which should be very familiar if you've seen other build systems.

For the most part, everything should be self explanatory to try out, or obvious enough to where you need to look
in the web documentation.  If you find something tricky, let us know, so we can improve the tutorial.

Intro: Projects & Builds
------------------------

Across the top of the homepage, you'll see all the types of objects in Vespene, the most important
being "Projects" and "Builds".

The default Vespene view shows the :ref:`projects` list, which you should be looking at now. A project represents a source code repository and/or a script to run.

A project might be named something like "build-foo-app" or "production-deployer" or "backup-database" or anything you want to launch from a web interface. 90% of
your projects are probably going to be source code builds, referred to in the industry as "CI", or "Continuous Integration", which has nothing to do with
Calculus, and thankfully so, because we've forgotten how to do math.

When projects are run, they create build objects.  Build objects track the status of the script execution, and can also be stopped or referred
to for status.  Builds have return codes and output.  Build history can be cleared per instructions in :ref:`cli`, so you don't have to worry about
thousands of build records piling up if you don't want to.

Builds can be triggered manually, but they don't have to.  You may wish to read about :ref:`webhooks` later, and builds can also be scheduled.

Vespene conviently shows the latest build for each project as well as a link to show all prior builds for a project.  You can also start and
stop project builds from this screen, but before we do that, let's talk a little bit about workers.

Intro: Workers & Worker Pools
-----------------------------

Builds are executed by :ref:`worker` nodes - processes that run on backend machines.

Worker Pools are essentially named queues with a bit of additional configuration.  A project gets to pick what worker pool handles its builds.  Commonly, a worker pool will represent a named build
environment like "Amazon Linux" or "FreeBSD", and on that worker, all the tools needed to run builds for that environment will be installed on that environment.
Even that is not even required in some cases, as you can also use a docker image to pull down your build environment. This is explained in more detail in the :ref:`worker`
documentation.

If your workers are going to represent automation, rather than source code building, each of these might be named after a region or environment where the script would be run from.

Because the tutorial is just a basic setup, the "tutorial_setup" command created a worker pool named "tutorial-pool", and the :ref:`setup` instructions
hopefully have a worker process running that will consume tutorial build requests.  You can check on this by looking at the supervisor configuration created in the /etc/vespene/ directory.

Before you start a project though, you will need to first use the superuser account to edit the configuration for this worker pool.  A sudo_user and sudo_password are set up, and these
may not be appropriate for your platform. Most likely they won't be! To ignore security for now,  you can just set these to the username running the Vespene worker, but you would
never do this in production.

For instance, in a development setup on my Mac, I often "cheat" and just set the sudo username to my current username, and then no password is even required.  That's not secure though, hence
why we don't want you to do that in production.  Remember to read the :ref:`security` instructions later.

Just to review, you should have started a process like this (either manually or with supervisor via the init scripts)::

     ssh-agent python manage.py worker tutorial-pool

While Vespene does also support :ref:`container_isolation`, like we mentioned, we will be using :ref:`sudo_isolation` for the tutorial.  In other words, don't touch the isolation setting
on the worker pool, just set the sudo user to something.

After changing the worker pool configuration you must restart the worker to get it to load the new configuration.

Keep these setting in mind should a build fail during the tutorial, it is probably because you need to adjust sudo settings and permissions.
The build scripts are otherwise not really complex, so that's really the only reason they might fail until you start tweaking them or adding builds of your own.

If the builds don't run at all (and stay in queued state), you probably don't have a worker pool running with the correct name.

If you are still stuck, hop by the forum (talk.vespene.io) and we'll try to help you through it.

Intro: Logins & SSH
-------------------

Projects often check out source code, and sometimes they do this with usernames and sometimes they use SSH keys.  We almost always prefer SSH keys for interacting
with git, but as not everyone may agree (that's fine), we support both.

There are seperate objects for this in Vespene.  A project may use only one Service Login, but can have multiple SSH keys.  These SSH keys will be available when
doing a checkout, but also when running any scripts - for instance, they are very useful for deployment scripts. Each of these are added to the UI using different
views in the web interface.  

The tutorial builds don't actually use any SSH keys, but setting them up should be self explanatory. Once you add an SSH key, you have to also configure
the project to use it in the UI. 

So first you set the SSH key object up, give it a name, and pick that name under the project settings.

The tutorial here doesn't actually check out any private repos, so it didn't bother setting any of that up.  We just wanted to make sure you knew
what this was about.

Hopefully that was an easy step, nothing to do, just some reading :)

Intro: Templates
----------------

Vespene build scripts can just be regular build scripts, but they can also be templated.

This is a major key feature of Vespene, but if you decide to never use templates, that's totally fine!

Why templates? In any large built system, the copy and pasting of build scripts can become a major problem.  Templates can help ensure commonality between build scripts and
make them easier to change. I've worked at a huge microservices setup in the past, and the ability to share pieces of text and variables between builds would have been
a life saver - but we didn't have anything like that.  Vespene is designed around making that better.

How does it work?

Within the scripts contained in a project, you can use {{jinja2}} template expressions to substitute variables and snippets, which
are large chunks of reusable text (which can also themselves be templates). See :ref:`variables` for more information.  If you have ever used
certain automation systems you may already know Jinja2.  If not, it is very similar to other web templating systems, like maybe erb or Django default 
templating.

Templating is all about substituting variables for text. Variables can be defined directly on a project or stage (which we'll discuss later) but also in reusable buckets of configuration variables called
Variable Sets.  If you want to use a lot of the same variables between multiple projects, Variable Sets and Snippets are the way to go.

As described in the variable documentation, variables are also written into the buildroot into a 'vespene.json' file, and can be a great way to pass parameters to external
programs that support JSON or YAML.

Large chunks of text can be reused with :ref:`snippets`, so there's a lot of power there too.

With this variable handling, Vespene can help you tame a build environment of 100s of microservices because we designed it for exactly that problem.

Intro: Pipelines
----------------

Pipelines are how continuous deployment workflows are implemented in Vespene.  

Pipelines configure a chain of builds, where if all builds in one stage become successful the subsequent builds will then activate automatically in parallel.  Each step of a pipeline is called a stage, and typical
stages are names like "build", "test", and "deploy".

Pipelines in Vespene are set up entirely using the web interface - no custom language or data format is required.

This topic is later explored fully in :ref:`pipelines`, but for now, we've just set up a pipeline you can click around and start.  It is not a good candidate of a real example, since
there isn't really any tests or deployment involved, but it shows how the builds chain into one another.

In the real world, steps in a pipeline would probably build some software, test it, deploy it to a stage environment, test it further, then maybe deploy it to production.

Intro: Triggers
---------------

Vespene :ref:`plugins` may include :ref:`triggers` that can be used for triggering chat notifications
and copying builds into published locations.  

If you want to notify your team members in Slack when a build runs or publish builds to s3, Triggers would be the way to go.

There are both pre build and post build triggers, and they are fed a large amount of JSON context about the builds when they run. Triggers can be written in any language
when using the command plugin, or can be implemented directly in Python.

When Can I Start Building Things?
---------------------------------

Thanks for being patient!

Earlier in the setup process you ran "python manage.py tutorial_setup", which pre-created several objects in Vespene.

These include:

* 5 example projects
* 1 pipeline
* 1 worker pool
* 3 user groups
* 2 variable sets
* 2 snippets
* 4 pipeline stages

We're now ready to explore these in a bit more detail.

This is a bit of a "free range" tutorial, expecting you to click around and read documentation to understand what everything does.

Manually Building A Project
---------------------------

To build a project, click the play icon on the project row.

Build the "minimal-project" now by clicking on the play icon.

Click the build number beside the project to see the status.

You'll note at this time the project doesn't auto-refresh because we haven't implemented websockets yet (coming!) - but that is coming.

Reload the build page and you should see the project is now queued. 

When the build process picks it up a worker will move it into "running" state.

You can click on the "builds" icon next to any project to see the build history of that project, or can just click on the current build to see 
the status of that particular build.

You can stop a project when it is in queued or running state by clicking the stop icon on either the project or build page.

The build will output content to the configured build root on each worker in settings.py.

If you want to notify someone when a build starts, succeeds, or fails, you can set that up using :ref:`triggers` later.
Vespene, for instance, ships with a basic Slack plugin. If you want to write a plugin that mails someone a postcard, that too is technically
possible with the right API.

Pipeline Experimentation
------------------------

Now that you've experimented with the example tutorial project, click over to the Pipelines view and then click the "map" icon by the pipeline.

:ref:`pipelines` are chains of builds, where if all builds complete in one stage, the rest of the builds trigger automatically.
While usuable for many things, pipelines are most notably the basis for continuous deployment in Vespene.

Normally we would expect to see :ref:`webhooks` automatically start our pipeline, but since this is just the tutorial we haven't set any up yet.

You will notice that running the first project in the pipeline, if they are successful, will run all the projects in the pipeline.

If the pipelines are still running, reload the page and you should eventually see all stages queue up and complete.

A Secret Lesson In Templates
----------------------------

So we've already mentioned templates, are there any examples of how to use them?

Our pipeline builds actually contained a hidden set of lessons about templates (if not somewhat arbitrary), which we'll talk about now.

Each build script for the pipeline teaches some lessons about templating.  Click on each project to read the build scripts, and then find the build output.

This will also give you a chance to get used to the navigation.

The variables in these builds are described in the comments of the build script, but you can see we are leveraging :ref:`variables`.

The build system also writes variables into a "vespene.json" file in the build root, so you can even use Vespene to globally define feature flags for your production applications.

Cleanup
-------

You can clean up and remove the objects the tutorial_setup script created whenever you like.

Run the setup command any time you like if you would like to restore them.

Next Steps
----------

The tutorial document was here to explain some basic concepts as you clicked around the Vespene UI.  Please check out the rest of the documentation on topics
that interest you to learn more.


