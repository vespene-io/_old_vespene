#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  importer.py - when each build runs, it can be wrapped
#  in an isolation procedure to prevent the build from doing "too many
#  dangeorus things".  This logic is maintained in 'plugins/isolation' and
#  can include a simple sudo before execution or building inside a container.
#  --------------------------------------------------------------------------

from datetime import datetime, timedelta
import os
import traceback
import shutil
import yaml

from django.db import transaction
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import Group
from django.db import transaction
from django.db import DatabaseError
from django.db.utils import IntegrityError

from vespene.common.logger import Logger
from vespene.common.plugin_loader import PluginLoader
from vespene.models.build import Build, RUNNING, SUCCESS, FAILURE
from vespene.models.project import Project
from vespene.models.worker_pool import WorkerPool
from vespene.models.pipeline import Pipeline
from vespene.models.stage import Stage
from vespene.workers import commands

LOG = Logger()

# =============================================================================

class ImportManager(object):

    def __init__(self, organization):
        self.organization = organization
        self.plugin_loader = PluginLoader()
        self.provider = self.get_provider()
        self.now = datetime.now(tz=timezone.utc)


    # -------------------------------------------------------------------------

    def get_provider(self):
        """
        Return the management object for the given repo type.
        """
        plugins = self.plugin_loader.get_organization_plugins()
        org_type = self.organization.organization_type
        plugin = plugins.get(org_type)
        if plugin is None:
            raise Exception("no organization plugin found: %s" % org_type)
        return plugin

    # -------------------------------------------------------------------------

    def needs_import(self):
        """
        An organization needs import if it is turned on, is configured to use THIS
        worker pool, and hasn't been imported too recently. The worker pool
        filtering was done in daemon.py already.
        """
        interval = self.organization.refresh_minutes

        if self.organization.active_build:
            return False
        if self.organization.last_build is None:
            return True
        if self.organization.force_rescan:
            return True

        end_time = self.organization.last_build.end_time
        delta = self.now - end_time
        minutes = delta.total_seconds() / 60.0
        return (minutes > self.organization.refresh_minutes)


    def make_working_dir(self, build):
        # FIXME: this is copied from builder.py and really should be moved into common code in workers/common.py
        # or something similar.
        #
        # TODO: this isn't cross platform yet but is seemingly more reliable than 'os' functions on OS X
        # will need to detect the platform and make the appropriate changes for Windows.
        path = os.path.join(settings.BUILD_ROOT, str(build.id))
        commands.execute_command(build, "mkdir -p %s" % path)
        commands.execute_command(build, "chmod 770 %s" % path)
        build.working_dir = path
        build.save()
        return path

    def make_stub_build(self):
        """
        Make a new empty build object to track the progress.
        We'll be logging some basic things to this object.
        It represents the import, not the projects about to be created
        or modified.
        """
        build = Build(
            project = None,
            organization = self.organization,
            status = RUNNING,
            worker_pool = self.organization.default_worker_pool,
            start_time = self.now
        )
        build.save()
        return build

    def finalize_build(self, build, failures):
        """
        Flag the build is done and update the organization
        to reference this.
        """
        now = datetime.now(tz=timezone.utc)

        if failures > 0:
            build.status = FAILURE
        else:
            self.organization.last_successful_build = build
            build.status = SUCCESS
        build.return_code = failures
        build.end_time = now
        build.save()
        self.organization.active_build = None
        self.organization.last_build = build
        self.organization.force_rescan = False
        self.organization.save()

    def find_all_repos(self, build):
        return self.provider.find_all_repos(self.organization, build)

    def clone_repo(self, build, repo, count):
        return self.provider.clone_repo(self.organization, build, repo, count)

    def read_vespene_file(self, build, path):
        """
        Return the data that would be in a .vespene, if it so exists
        """
        path = os.path.join(path, ".vespene")
        if os.path.exists(path):
            fh = open(path)
            data = fh.read()
            fh.close()
            return yaml.safe_load(data)
        return None

    def get_defaults(self, build, repo):
        """
        There is only a very minimal set of .vespene info for projects that don't
        specify anything. There's good reason for this - we want to use the ORM
        defaults.  This makes some fields requierd because the ORM will choke
        if they are not set - like the worker_pool!
        """
        repo_ending = repo.split("/")[-1]
        defaults = dict(
            name = repo_ending,
            script = "",
            webhook_enabled = True
        )
        return defaults

    def find_project(self, build, repo):
        """
        See if we can find the project based on the repository address. The
        project name specified in the .vespene file is given ZERO authority to prevent
        manipulation of other repo configurations.
        """
        projects = Project.objects.filter(repo_url=repo)
        if projects.exists():
            return projects.first()
        else:
            return None

    def adjust_database_config(self, build, project, repo, config, path):
        """
        We have determined what the .vespene file says, mixed
        in with any defaults. Now look at the policy of the organization
        and decide what attributes we can set, and manipulate
        the ORM model to match.
        """

        project_name = config['name']

        if project is None:

            qs = Project.objects.filter(name=project_name).exclude(repo_url=repo)
            if qs.exists():

                # ok so we found a project matching the repo, but the name is wrong.  Attempting to set the name *WILL* fail due to DB constraints
                # while we could generate a name, it would add database clutter and this corner case shouldn't be too common
                # so just abort the import process
                self.log(build, "another project already exists with the name chosen but a different repo address, please rename them to match or remove the name the .vespene file")
                return     

            project = Project(
                repo_url = repo, 
                name = project_name,
                scm_type = 'git',
                worker_pool = self.organization.default_worker_pool
            )

        org = self.organization

        if project.scm_login is None:
            project.scm_login = self.organization.scm_login

        # -----------------------------------------------
        # various helper functions to allow loading from the .vespene
        # config structure and then saving results on the ORM models

        def attr_manage(key):
            value = config.get(key, None)
            if value is not None:
                setattr(project, key, value)

        def m2m_manage(attribute, model):
            relation = getattr(project, attribute)
            original_names = [ x.name for x in relation.all() ]
            set_names = config.get(attribute, None)
            if set_names is None:
                return

            for name in set_names:
                if name not in original_names:
                    obj = model.objects.filter(name=name)
                    if obj.exists():
                        relation.add(obj.first())
            
            for name in original_names:
                if name not in set_names:
                    obj = model.objects.filter(name=name)
                    if obj.exists():
                        relation.remove(obj.first())

        def fk_manage(attribute, model):
            if attribute not in config:
                return
            value = config.get(attribute)

            objs = model.objects.filter(name=value)
            if not objs.exists():
                self.log(build, "object of type %s not found: %s " % (type(model), value))
                return
            obj = objs.first()
            setattr(project, attribute, obj)

        # --------------------------------------------------
        # apply the config file settings, using defaults if needed

        if org.overwrite_project_name and config['name']:
            project.name = config['name']

        if org.overwrite_project_script and config['script']:
            script = config['script']
            script_path = os.path.join(path, script)
            if os.path.exists(script_path):
                fh = open(script_path)
                data = fh.read()
                fh.close()
                project.script = data
            else:
                self.log(build, "build script as referenced in .vespene is missing: %s" % script)
        

        # bookmark:
        # what should we do with script setting if no .vespene?
        #elif org.overwrite_project_script and not project.script:
        #    project.script = "#!/bin/bash\necho \"build script not configured\""

        if org.allow_worker_pool_assignment:
            fk_manage('worker_pool', WorkerPool)

        attributes = [ 'timeout', 'container_base_image', 'repo_branch', 'webhook_enabled', 'launch_questions', 'variables']
        if org.overwrite_configurations:
            for attribute in attributes:
                attr_manage(attribute)

        project.save()

        if org.overwrite_configurations:
            # the permissions controls in the Organization object for these managers could be split
            # up in future versions
            fk_manage('pipeline', Pipeline)
            fk_manage('stage', Stage)
            m2m_manage('owner_groups', Group)
            m2m_manage('launch_groups', Group)

        project.save()
        return project

    # -------------------------------------------------------------------------

    def log(self, build, msg):
        build.append_message(msg)

    # -------------------------------------------------------------------------

    def import_single_repo(self, build, repo, count):

        # clone the repo into the build root and return the path
        # chosen, which will append on the build number just like
        # the other regular builds

        self.log(build, "begin repo import: %s" % repo)
        
        path = self.clone_repo(build, repo, count)

        # find the project by looking up the repo address
        # if not found, this will create the project and try to give it
        # a decent name based on the repo, or using the .vespene
        # file if it exists (this is sorted out later)

        project = self.find_project(build, repo)

        # see if there is a .vespene (YAML) config in the repo (consult web docs
        # on import features)

        self.log(build, "project id: %s" % project)
        config = self.read_vespene_file(build, path)

        has_dotfile = True
        if config is None:
            if not self.organization.import_without_dotfile:
                self.log(build, ".vespene file is missing, skipping")
                return
            has_dotfile = False
            config = dict() 
        

        # have some defaults for certain parameters, but not others. 
        # why? mostly we want to use the ORM defaults. Here we just enable
        # the webhook and have a default name in case it isn't set. 

        defaults = self.get_defaults(build, repo)

        # the calculated config is the merging of the actual config with the defaults
        # the .vespene file will win out.
        defaults.update(config)
        config = defaults
        self.log(build, "applying config: %s" % config)

        # now we modify the project object, whether created or loaded

        project = self.adjust_database_config(build, project, repo, config, path)   

        # the import of this particular repo is done, but we have more to do in the
        # organization.  Clean up the buildroot to save space, and then keep trucking

        shutil.rmtree(path)
        self.log(build, "complete\n")

    # -------------------------------------------------------------------------

    def do_import(self):
        """
        main logic of the .vespene github organization import code
        """

        # FIXME: disabled for development only!

        if not self.needs_import():
            # skip organizations that are already up to date or are disabled
            return

        # create a dummy build object so we can track the progress
        # this is a "special" build in that it tracks an organization and
        # not a project (it does MODIFY other projects, don't get confused
        # about that.. it's not buildilng any projects)

        build = self.make_stub_build()
        build.working_dir = self.make_working_dir(build)
        self.log(build, "begin organizational import, scratch space: %s" % build.working_dir)

        # find all the repos in the organization, using the organization plugin
        # for instance, vespene.plugins.organizations.github

        repos = self.find_all_repos(build)

        failures = 0
        count = 0
        for repo in repos:
            try:
                self.import_single_repo(build, repo, count)
                count = count + 1
            except DatabaseError as dbe:
                traceback.print_exc()
                self.log(build, str(dbe))
                transaction.rollback()
                failures += 1
            except Exception as e:
                build.append_output("ow: repo processing failure, moving on with the next one...")
                traceback.print_exc()
                build.append_output(str(e))
                # FIXME: DEVELOPMENT ONLY!
                self.log(build, "repo import failed")
                failures += 1

        # mark the build object as completed.  Ordinarily we should flag if there
        # are any errors, but we're mostly trying to be fault tolerant.

        self.finalize_build(build, failures)

        # since the build root itself won't have anything meaningful in it, we can
        # also throw away the (should be empty) directory at this time.

        shutil.rmtree(build.working_dir)


