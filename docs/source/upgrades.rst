.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _upgrades:

********
Upgrades
********

Vespene upgrades always preserve data through use of built-in database migrations. 

The upgrade process for Vespene is as follows:

Web nodes

(1) Update the code on all nodes.

Database
========

(2) Run "make migrate" on exactly one machine with database access
to apply any database schema changes.

Restart nodes
=============

(3) Restart the webserver and worker processes

If using systemd and the production setup::

    # systemd restart vespene.service

If not, just stop supervisord and restart it

Verify
======

(4) Make sure everything is happy by logging into the interface
and running a build or two. Make sure it is successful.



