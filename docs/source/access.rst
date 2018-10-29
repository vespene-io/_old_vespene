
.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _access:

***************************
SSH Keys and Service Logins
***************************

Vespene can store SSH private keys as well as service logins (such as GitHub username and passwords) to use during builds and checkouts that occur
as part of builds. This means users using Vespene don't have to provide these credentials (or have direct access to them) and the system will use them on their behalf.

.. _ssh:

SSH Keys
--------

Vespene can manage SSH keys in two ways.

In the simplest case, when checking out repositories, such as git repos, Vespene can use SSH keys on your behalf during the checkout.  
Using dedicated SSH keys is often preferable to using usernames or passwords for these services.

Further, when running projects, Vespene workers can use SSH keys to allow access to external systems. This is perhaps more interesting. For instance,
a Vespene worker could use an SSH key to manage an external server or set of servers.

Multiple SSH keys can be assigned to any project.  They are entered in the "SSH Keys" view of Vespene, and then selected in the Project UI.
Each key does require a private key upload, as well as an unlock password if the key is protected.

The contents of the keys do not have to be shared with users who can access the Vespene UI, but they can still use them when launching the project.

SSH keys uploaded *ARE* private keys, which are stored using Vespene encryption plugins in the database. 

Build isolation as described in :ref:`workers` is used to prevent the build scripts from accessing the database.  As described in more detail in 
:ref:`security`, SSH keys given to Vespene should be deploy keys exclusively used by the Vespene system only, and frequently rotated. Key management
may be modified in a future release. Keys given to Vespene should be unique for the purpose of use *by* Vespene to enable easy rotation.

To use SSH keys it is required that workers are started wrapped with the 'ssh-agent' process, as described in :ref:`workers` and this is done automatically
if you generate Vespene's supervisor config as according to the :ref:`setup` instructions.

Also note that there is no differentiation between SSH keys provided for access to a SCM or a machine, both are available for both purposes. If this is concerning,
provide dedicated keys for specific purposes.

.. _service_logins:

Service Logins
--------------

Service Logins are sets of usernames and passwords that can be used to access source control repositories.

The system will not share the passwords used, but they are made available to multiple users.

For source control systems that also work with SSH keys, like git, these can also be ignored in favor of :ref:`ssh`.

At this time, Service Logins are *only* used during git checkouts and Subversion requires a publically accessible repo.  Updates to these
behaviors are welcome contributions.

These passwords are not yet marked by a particular service, for instance they can't be used for cloud API logins or something like that.  This could
also be implemented in the future.


