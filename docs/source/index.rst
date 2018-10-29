.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: left

.. _about:

Vespene
-------

Vespene is a modern, streamlined build and self-service automation platform. Vespene is 
designed to combat chaos in complex software development and operations environments.

Our mission is simple: get great people together to build the ultimate system we all want to use.

.. image:: projects1.png
   :alt: Vespene Projects Screen
   :align: left

Architecture
============

Vespene is a horizontally-scalable Python application, using Django and PostgreSQL. Each node in a Vespene cluster runs a copy of the web code
and any number of backend build "worker" processes, all of which share the database. Users can connect to any node in the cluster.

Continuous Integration
======================

While equally usable for small shops, Vespene was inspired by the needs of large organizations with hundreds of microservice projects in dozens of languages. 

When organizations start to have too many projects, they need an easy way to share values and code snippets between those projects. To support this we have Jinja2 templating of build scripts via :ref:`variables` built-in. Variables can be defined across multiple hierarchies of objects throughout Vespene, and are also directly consumable by loading "vespene.json" from the build root, which interfaces nicely with any application that can read YAML or JSON. 

As you might expect of any build system, builds can be launched manually, triggered from commits with :ref:`webhooks`, or set off on timers with :ref:`scheduling`.

Automation, "DevOps", Etc
=========================

Projects in vespene don't need to just represent source code. Projects can also launch automation scripts or software of any kind, whether being pulled from source control or just scripts defined in Vespene. These jobs can include security scans, cloud topology changes, database backups, launching functional tests, and more.

While not all automation tools are SSH-powered, many are. Vespene can memorize important :ref:`ssh` keys and use them on your behalf, using built-in support for ssh-agent.

Helping with the self-service magic, projects can ask interactive questions before they are launched with :ref:`launch_questions`, providing unpriveledged users a simple interface to invoke specific tasks without needing full shell access. These questions can be drop-downs, multiple choice, or fill in the blank.

Continuous Integration
======================

Vespene features :ref:`pipelines` to construct complex CI/CD topologies - successful builds can trigger other builds, in serial or parallel.  Unlike some other CI tools, pipelines in Vespene are easily and graphically configured, and there is no custom DSL ("Domain Specific Language") to learn and debug. Use pipelines to implement fully automated deployment to production, or just stop at staging - whatever you feel comfortable with.

Admin-Focused
=============

Another key inspiration was Vespene was frustration with setup, configuration, and maintaince of other CI/CD platforms.

Vespene is also straightforward to :ref:`setup` and maintain. GitHub organizations can be sucked in automatically, and configured with ".vespene" files (see :ref:`importing`). From an admin perspective, there are no message queues or clunky leader election clusters to keep running, and every node in the cluster has the same configuration.

Extensibility
=============

Finally, Vespene has an exceptionally concise and extensible codebase. Nearly all policy in Vespene is implemented in :ref:`plugins`, and more areas for pluggability will be added over time. 

Status
======

Vespene aims to be usable on the master branch and welcomes feedback, testing, new features, and ideas of all kinds.
Database migrations will always preserve your data, even during development.

Officially, Vespene is in beta as it just came out! We are shooting for our first stable release in early January of 2019 and are likely going to do releases about every three months thereafter.

Next Steps
==========

Whether you have a classic deployment setup or are going all-in on microservices and need to tame the sprawl, we hope Vespene will be the build system for you.  If it's not yet, we're always improving and on the lookout for new ideas.  Things are new, flexible, and everything is up for discussion.

Want to try things out? Read the :ref:`setup` instructions then the :ref:`tutorial`. Send us your feedback and let's work together to make something great.

Links
=====

* `Forum <http://talk.vespene.io>`_ - user and developer conversation
* `GitHub <http://github.com/vespene-io/vespene.>`_ - code checkouts, pull requests, and bug reports
* `Homepage <http://vespene.io>`_ - homepage, low-traffic announcement list signup
* `@vespene_io <http://twitter.com/vespene_io>`_ and `@laserllama <http://twitter.com/laserllama>`_ - twitter


