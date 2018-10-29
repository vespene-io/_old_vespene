.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _security:

**************
Security Guide
**************

Securing a build system is important, all of your code runs through your build system and the build system
often has priveledged access to other parts of your environment.  Some build systems are more secure than
others, and your approach to security may vary based on your concerns about insider threat security.

Vespene was largely designed with security in-mind, but can always be improved. If you have security
concerns that may effect production deployments, please contact michael@michaeldehaan.net to discuss them.

Here are some tips to keep Vespene configured more securely and prevent unwanted surprises.

Do Not Put Your Build System On The Public Internet
---------------------------------------------------

With the exception of routing :ref:`webhooks` (likely through an intermediate server), Vespene should not be publically accessible on the
open internet. If you take most modern build systems you can find public instances of them through things
like shodan, and this should be considered quite alarming. The ability to take over a build system
allows manipulation of production code inside organizational environments, and can be devastating.

If you want to use webhooks, consider forwarding webhooks posts intelligently through a public server you do control, only
allowing them from known sources, and do not make Vespene entirely public.

Limit The Number of Admin Users
-------------------------------

Most users don't need admin (superuser) access.

When users are not given admin access, they are subject to access control as described in :ref:`access`, which
has some very good reasonable defaults.

Admin access should be given out only to users you trust.

Disable The Admin View
----------------------

While not a security consideration per se, the admin view allows direct database manipulation that bypasses
a large amount of business logic in the application.  Editing in the admin view should almost never
happen, though it is ok to use the admin view to delete objects.

If you want to discourage users from manually editing database results, it may be adviseable to disable
the Django admin view in settings.

Superusers in the main application will still have full access.

Isolation Methods for Worker Pools
----------------------------------

Vespene [Worker Pools](workers.html) have configurable isolation modes for security reasons.

If you have docker installed, the "Basic Container" isolation mode will be the easiest to set up.

When using this mode, the base container image for the build is set *per project*, and the sudo
settings on the worker pool are ignored.  Right now there isn't a whitelist of what images users can choose
for base images, so technically they could build based on any image in Docker Hub or a private registry
the docker-CLI has access to. This may change in the future to be something that is web-configurable.

If using the sudo isolation mode *instead*, it is strictly vital that the sudo_user chosen does not
have read access to the Vespene configuration files, to avoid build scripts obtaining database
access.  In particular, during the setup process you probably generated secrets via "make secrets" (aka
"python manage.py generate_secrets").  This command writes files into /etc/vespene/settings.d/secrets. 

These files are used to decrypt secrets in the database when using the basic encryption plugin that ships
with Vespene.

No Multi-tenancy
----------------

Vespene was intentionally NOT designed for multi-tenancy between potentially competing organizations.

Instead install a seperate isolated Vespene for each organization.

While this is technically possible to do, it would be a huge time-suck and bloat the code in ways we'd rather
not deal with it, and would likely not be something 99% of users would use. Instead, deploy a seperate
Vespene cluster for each tenant if you want to accomplish that level of organizational isolation.

Secret Encryption and the Database
----------------------------------

As mentioned earlier, the default configuration for Vespene uses symetric encryption to keep from storing
SSH keys, unlock passwords, and SCM logins in raw plaintext.  The key to unlock these passwords is in /etc/vespene/settings.d/secrets.py
and must be available on all machines in the cluster.

Be aware of who can access this file and do not allow the build sudo_user as configured on the Worker Pool object
to read it, lest the build system itself be used to retrieve the contents of this file.

Similarly, you want to make sure the build sudo user does not have access to read the database connection info in settings.d as well,
as this would allow directly mucking with the database.

When using worker pools with container isolation, this is also not a concern.

Only admins have the ability to configure worker pools so there is no mechanism for regular users to change the sudo user that runs
their builds.

The encryption mechanism is in fact pluggable if you want to use another method.

Lock Down PostgreSQL
--------------------

In a secure configuration, only the Vespene web interface nodes and the worker nodes should be able to connect to 
PostgreSQL.

This is a network/firewall and database authentication issue and is a responsibility of the administrator.

A database administrator will only be able to read encrypted versions of keys and passwords.

If your database administrator, or those with access to database backups, has access to the Vespene secrets file and the database this should be considered
under an insider threat scenario.

Understand Variables/Snippets Values are Semi-Public
----------------------------------------------------

Variables in Vespene (as opposed to secrets, like passwords) are more or less public.

Don't store passwords in "variables" or "Variable Sets" inside of Vespene unless you don't mind all users of Vespene
and the associated projects being able to read them.

These values are available for anyone with a login, and if the buildroots are made more public (for instance, made available over
NFS or HTTP or FTP), those variable files are also accessible in the build root.

Climbout
--------

If using the sudo isolation, one build script will be able to write into the build root of another.

Use the basic_container isolation mode if you want to avoid this.

It's generally not a problem that one developer might try to pollute the build directories of another build, but it is technically
possible, and is possible in most production build systems.

Projcet Insertion and Spamming
------------------------------

In the stock configuration any user can create any number of objects, because we trust users who are given access to Vespene
are employees who have important business reasons for accessing the service.  While they cannot edit objects they do not have
rights to, it does mean granting access to 3000 people to create projects could result in a degree of disorganization.

It is certaintly true that a user who can create projects has, just like a user who has access to a source code repository,
access to make the build system run certain commands in the environment where workers run.

Limiting access to creation of certain types of objects to certain groups of users can be controlled with the "group_required"
plugin.

For instance, it might be redesirable to use the "group_required" plugin to only allow Developers, QA, and Ops to create projects
in Vespene, while users in the "Support" pool may only be able to run jobs where they have been added to the launch group
for that particular project.

Dependency Exploits
-------------------

This vulnerability is possible in ALL build systems, and a bit of a stretch, but it was worth bringing up.

What if a software dependency you are using is compromised?

It could mail your code somewhere, or use your build machine to do some forms of evil.

If this is a concern, consider vendoring all of your 3rd party libraries or using mirroring software.

Also limit what network resources your build machines can access.

SSL
---

You should consider fronting Vespene's webserver with NGINX or Apache to provide https:// access.
This is not provided if you are just accessing Vespene on port 8000, and we did not want to require Apache
vs NGINX for all users because users have specific preferences.

If you do proxy requests through, we recommend routing "/" on port 80 to "/" on port 8000 to keep things completely
simple, and not running other web applications on the Vespene box.

Vespene isn't really coded to make the URL pattern adjustable at this time.

Found a Security Bug Not Mentioned Above?
-----------------------------------------

Please email michael @ michaeldehaan.net with details and we'll work to address it quickly.

The same goes for suggestions to this guide. Thank you!

