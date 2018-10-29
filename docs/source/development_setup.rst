
.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _development_setup:

*****************
Development Setup
*****************

The :ref:`setup` guide details production deployment setup of Vespene, but this document talks about
developer setup.

Vespene can be developed easily on any Linux/Unix system or OS X.  The core application primarily *is* developed
on OS X.  Where those setup processes deviate from Linux, we'll call those steps out.

Git Checkout
------------

First grab the master branch from github::

   git clone https://github.com/vespene/vespene

OS X Python 3.X Setup
---------------------

You'll need a newer Python but this is easy. Vespene is written for Python 3.7 or greater.

For OS X, this is easy to install from homebrew. For other operating systems substitute
the appropriate commands to install Python 3::
    
    brew install python

Vespene also uses the timeout command, which you can get from coreutils as 'gtimeout'::

    brew install coreutils

You will then want to make sure Python 3 is in your path, if not already, for example::

    # vim ~/.bashrc
    export path=/usr/local/bin:$PATH
    alias python /usr/local/bin/python3

This may change a bit depending on what your distribution calls Python 3.  If you are on CentOS for example,
python3 is available in yum, if you install the "epel-release" package.

Activate your new path::

    source ~/.bashrc

Now install virtualenv so your Python installation can download dependencies locally, instead
of globally::
    
    easy_install-3.7 virtualenv
    virtualenv env -p /usr/local/bin/python3

And now activate the virtualenv::    

    source env/bin/activate

Future commands you run while this virtualenv is active will automatically use the right python.
If you start new terminal windows, don't forget to activate the virtualenv, or missing dependnecies
will cause errors to pop up.

OS X Keychain
-------------

In a very specific example of invalid project setups (where the https:// username is not provided), Mac worker
builds can go interactive.

To disable this, run the following::

    git credential-osxkeychain erase

Then type in the following::

    host=github.com
    protocol=https
    [Press Return]

This will not happen in Linux/Unix environments.

Other Dependencies
------------------

Vespene can isolate builds using either sudo or docker. 

If you are working on the worker code, you'll probably want to go ahead and install docker, as even if you use it doesn't hurt much.
We don't actually use docker for anything in the development or deployment process, just as a utility to constrain build environments.

If on a Mac, find and install "Docker for Mac" and the docker support will be fully functional just
like the Linux version.

Python Dependencies
-------------------

From the checkout directory, once the virtualenv is activated::

    make requirements

This step isn't OS X specific. You'll probably need gcc though, if you don't have it and are on a Mac,
you can get it from homebrew::
 
    brew install gcc

PostgreSQL Database Setup
-------------------------

You'll need to install PostgreSQL first if you haven't already.  I like Postgresql.app for Mac development
but the database can run anywhere.

From a working PostgreSQL installation, create a new database::

    # createdb vespene

Next we'll need to create a user that can interact with the database::

    # psql

From the postgresql shell::

    # CREATE USER vespene WITH PASSWORD 'your-password';
   
Grant the vespene user full access to the PostgreSQL database::

    > GRANT ALL PRIVILEGES ON DATABASE "vespene" to vespene;

Remember the password used above.

Django Setup
------------

Since Vespene is a Django app, the configuration file is in Python format.

Add the following content in something like /etc/vespene/settings.d/database.py or (in the checkout) vespene/local_settings.py, neither
of which probably exists on your filesystem yet::

    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'vespene',
                'USER': 'vespene',
                'PASSWORD' : 'your-password',
                'HOST': 'localhost',
                'ATOMIC_REQUESTS': True
            }
    }

These settings will also need to be copied to other workers if you are testing a multi-node setup.

Also add an entry describing where the temporary build root should be for builds occuring on this system, perhaps in
/etc/vespene/settings.d/workers.py::

    BUILD_ROOT = "/tmp/vespene/build_root"

The path can be any path, but it must exist and be writable by the user running the worker process, and if so
configured, the sudo_user set as described in :ref:`workers`::

	mkdir -p /tmp/vespene/build_root

Database Schema
---------------

Once the database and settings.py have been configured, run the migration step from your checkout directory to create
the initial database tables::

	make migrate

This command is also used later for database upgrades and can be re-run at any time.

Directory Structure
-------------------

Normally created by the setup automation, the following directories need to be created::

    mkdir -p /etc/vespene/settings.d
    mkdir -p /var/log/vespene

Secret File
-----------

Vespene has some built-in encryption of database secrets, and also needs a Django secret key.  To create this run::

    make secrets

This file is saved in /etc/vespene/settings.d/secrets.py and should never be checked into source control.  Permissions on
this file are discussed in :ref:`security`.

Superuser Account
-----------------

You will also need to create a superuser account for the Vespene administrator user. Remember the username and password you choose:

    python manage.py createsuperuser

Testing
-------

You may now run the development-mode webserver::

    python manage.py runserver

See if you can login at http://127.0.0.1:8000/ with the username and password you chose.

Tutorial Setup
--------------

Want to use the tutorial?

To make the objects the tutorial needs, run::

   python manage.py tutorial_setup

This command will not ask any questions and just primes the system with some sample objects.

This will create a worker pool named "general", which is enough to run a worker
in the next step.

We will go ahead and set up that worker process.

Worker Setup
------------

Workers can be run on any machine and you can have any number of them.  These are the distributed processes that
actually perform the builds.

Workers use the exact same code and settings used for the web application, and access the same database server.

To run a worker, launch the process as follows::

	ssh-agent python manage.py worker <worker-pool-name>

For instance, now that we have a worker pool named general:

	ssh-agent python manage.py worker general

This starts 1 new worker process on the machine, severing the pool named "general".  The process will log
to the foreground.

The 'ssh-agent' wrapper command allows Vespene to handle SSH key additions automatically and is required.

Plugins are run both on the worker and the client, depending on the plugin, so when you start
reading about `plugins`, be aware you'll need to apply some of those changes on the workers.

Production installations use supervisord to corral multiple worker processes, as described in :ref:`setup`.

Development Upgrades
--------------------

Once you are up and running, if you pull down a new version of the source code, you may find that 
dependencies have changed or there are migrations to apply.

On each machine in a cluster::

    make requirements

Once::

    make migrate

Then you can bounce your processes and will be good to go.



