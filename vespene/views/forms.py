#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  forms.py - used to set up Django forms for all the human-views
#  throughout the application. 
#  --------------------------------------------------------------------------

from vespene.models.ssh_key import SshKey
from vespene.models.service_login import ServiceLogin
from vespene.models.project import Project
from vespene.models.build import Build
from vespene.models.pipeline import Pipeline
from vespene.models.stage import Stage
from vespene.models.snippet import Snippet
from vespene.models.variable_set import VariableSet
from vespene.models.worker import Worker
from vespene.models.worker_pool import WorkerPool
from vespene.models.organization import Organization
from vespene.common.plugin_loader import PluginLoader
from vespene.manager import Shared

from django import forms
from django.contrib.auth.models import User, Group
from django.db.models import Q
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.layout import Layout
from crispy_forms.helper import FormHelper

PLUGIN_LOADER = PluginLoader()
ISOLATION_CHOICES = PLUGIN_LOADER.get_isolation_choices()
SCM_CHOICES = PLUGIN_LOADER.get_scm_choices()
ORGANIZATION_CHOICES = [['github','github']]

class BaseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):        
        super(BaseForm, self).__init__(*args, **kwargs)

    def make_read_only(self):
        for x in self.Meta.fields:
            self.fields[x].widget.attrs['disabled'] = True
        return self

class StageForm(BaseForm):
    class Meta:
        model = Stage
        fields = ('name', 'description')

    def __init__(self, *args, **kwargs):
        super(StageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'name', 'description')
            )
        )

class PipelineForm(BaseForm):
    class Meta:
        model = Pipeline
        fields = ('name', 'description', 'enabled', 'owner_groups',
            'stage1', 'stage2', 'stage3', 'stage4', 'stage5', 'stage6', 'stage7',
            'last_completed_date', 'last_completed_by', 'variables', 'variable_sets',
        )     
        widgets = {
           'owner_groups' : forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super(PipelineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'name', 'description', 'enabled'),
                Tab('Stages', 'stage1', 'stage2', 'stage3', 'stage4', 'stage5', 'stage6', 'stage7'),
                Tab('Variables', 'variable_sets', 'variables'),
                Tab('Ownership', 'owner_groups')
            )
        )       

class ProjectForm(BaseForm):

    scm_type = forms.ChoiceField(choices=SCM_CHOICES)

    class Meta:
        model = Project
        fields = ('name', 'description', 'pipeline', 'pipeline_enabled', 'stage', 'script', 'timeout', 'variables', 
            'scm_type', 'repo_url', 'repo_branch', 'scm_login', 'ssh_keys', 
            'owner_groups', 'variable_sets', 'worker_pool', 'webhook_enabled', 'webhook_token',
            'container_base_image', 'launch_questions', 'launch_groups',
            'schedule_enabled','monday','tuesday','wednesday','thursday','friday',
            'saturday','sunday','weekday_start_hours','weekday_start_minutes','weekend_start_hours',
            'weekend_start_minutes','schedule_threshold')

        # TODO: improve formatting of all script and variable field editors
        widgets = {
           'script': forms.Textarea(attrs={'rows':20, 'cols':80}),
           'launch_groups' : forms.CheckboxSelectMultiple(),
           'owner_groups' : forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'name', 'description'),
                Tab('Script', 'script', 'timeout', 'container_base_image'),
                Tab('Repository', 'scm_type', 'repo_url', 'repo_branch', 'scm_login', 'webhook_enabled', 'webhook_token'),
                Tab('Schedule', 'schedule_enabled','monday','tuesday','wednesday','thursday','friday',
                    'saturday','sunday','weekday_start_hours','weekday_start_minutes','weekend_start_hours',
                    'weekend_start_minutes','schedule_threshold'),
                Tab('SSH', 'ssh_keys'),
                Tab('Variables', 'variable_sets', 'variables', 'launch_questions'),
                Tab('Environment', 'worker_pool'),
                Tab('Pipeline', 'pipeline_enabled', 'pipeline', 'stage'),
                Tab('Ownership', 'launch_groups', 'owner_groups')
            )
        )
        request = Shared().request
        if not request.user.is_superuser:
            gids = [ g.id for g in request.user.groups.all() ]
            # this filtration is a little specific to the ownership plugin for authz and we might want to make this more pluggable later
            self.fields['scm_login'].queryset = ServiceLogin.objects.filter(Q(owner_groups__pk__in=gids) | Q(created_by=request.user))
            self.fields['ssh_keys'].queryset = SshKey.objects.filter(Q(owner_groups__pk__in=gids) | Q(created_by=request.user))
   
class OrganizationForm(BaseForm):

    organization_type = forms.ChoiceField(choices=ORGANIZATION_CHOICES)

    class Meta:
        model = Organization
        fields = ('name', 'organization_type', 'description', 'organization_identifier', 'api_endpoint', 'import_enabled', 'import_without_dotfile', 'default_worker_pool', 
        'refresh_minutes', 'force_rescan', 'scm_login', 'worker_pool', 'created_by',
        'overwrite_project_name', 'overwrite_project_script', 'overwrite_configurations', 'allow_worker_pool_assignment', 'auto_attach_ssh_keys')
        widgets = {}

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'name', 'description'),
                Tab('Import Configuration', 'organization_type', 'organization_identifier', 'api_endpoint', 'scm_login', 'import_enabled', 'refresh_minutes', 'force_rescan'),
                Tab('Import Rules', 'import_without_dotfile', 'default_worker_pool', 'overwrite_project_name', 'overwrite_project_script', 'overwrite_configurations',
                'allow_worker_pool_assignment', 'auto_attach_ssh_keys'),
                Tab('Environment', 'worker_pool')
            )
        )
        request = Shared().request
        if not request.user.is_superuser:
            # currently you can only be superuser so this code is a little defensive and is taken from *ProjectForm*
            gids = [ g.id for g in request.user.groups.all() ]
            # this filtration is a little specific to the ownership plugin for authz and we might want to make this more pluggable later
            self.fields['auto_attach_ssh_keys'].queryset = ServiceLogin.objects.filter(Q(owner_groups__pk__in=gids) | Q(created_by=request.user))
            self.fields['ssh_keys'].queryset = SshKey.objects.filter(Q(owner_groups__pk__in=gids) | Q(created_by=request.user))
      


class BuildForm(BaseForm):
    
    class Meta:
        model = Build
        fields = ('project', 'revision', 'revision_username', 'return_code', 'start_time', 'end_time', 'status', 'output', 'messages', 'working_dir', 'variables', 'script',
        'launch_answers', 'output_variables', 'pipeline_parent_build_id', 'pipeline_origin_build_id', 'queued_time', 'worker')
        widgets = {
          'output': forms.Textarea(attrs={'rows':20, 'cols':80}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)  
        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'project', 'status', 'revision', 'revision_username', 'queued_time', 'start_time', 'end_time', 'return_code'),
                Tab('Script', 'script'),
                Tab('Output', 'output', 'messages'),
                Tab('Debug', 'worker', 'working_dir', 'variables', 'launch_answers', 'output_variables', 'pipeline_parent_build_id', 'pipeline_origin_build_id')
            )
        )

class SnippetForm(BaseForm):

    class Meta:
        model = Snippet
        fields = ('name', 'description', 'text', 'owner_groups')
        widgets = { 
           'owner_groups' : forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'name', 'description'),
                Tab('Text', 'text'),
                Tab('Ownership', 'owner_groups')
            )
        )

class VariableSetForm(BaseForm):

    class Meta:
        model = VariableSet
        fields = ('name', 'description', 'variables', 'owner_groups')
        widgets = {
           'owner_groups' : forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'name', 'description'),
                Tab('Variables', 'variables'),
                Tab('Ownership', 'owner_groups')
            )
        )

class SshKeyForm(BaseForm):

    unlock_password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = SshKey
        fields = ('name', 'description', 'private_key', 'unlock_password', 'owner_groups')
        widgets = {
           'owner_groups' : forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'name', 'description'),
                Tab('Access', 'private_key', 'unlock_password'),
                Tab('Ownership', 'owner_groups')
            )
        )

class ServiceLoginForm(BaseForm):

    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = ServiceLogin
        fields = ('name', 'description', 'username', 'password', 'owner_groups')
        widgets = {
           'owner_groups' : forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)    
        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'name', 'description'),
                Tab('Access', 'username', 'password'),
                Tab('Ownership', 'owner_groups')
            )
        )    

class WorkerPoolForm(BaseForm):
    
    sudo_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    isolation_method = forms.ChoiceField(choices=ISOLATION_CHOICES)

    class Meta:
        model = WorkerPool
        fields = ('name', 'variables', 'variable_sets', 'isolation_method', 'sudo_user', 'sudo_password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'name'),
                Tab('Variables', 'variable_sets', 'variables'),
                Tab('Security', 'isolation_method', 'sudo_user', 'sudo_password')
            )
        )


class UserForm(BaseForm):

    class Meta:

        password = forms.CharField(label="password", required=False, widget=forms.PasswordInput())
        groups = forms.CheckboxSelectMultiple()
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'is_superuser', 'groups' )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['password'] = ''
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'username', 'first_name', 'last_name', 'email'),
                Tab('Access', 'password', 'groups', 'is_superuser'),
            )
        )
        self.fields['password'].required = False
        self.fields['password'].widget = forms.PasswordInput()

        obj = kwargs.get('instance', None)
        user = Shared().request.user
        if obj:
            # this applies only to the edit form
            if obj != user and not user.is_superuser:
                # only superusers can edit passwords of other users
                self.fields['password'].widget.attrs['disabled'] = True
            elif not user.is_superuser:
                # only superusers can toggle the superuser bit and groups on any account
                for field_name in [ 'is_superuser', 'groups' ]:
                    self.fields[field_name].widget.attrs['disabled'] = True

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        new_pass = self.cleaned_data["password"]
        if new_pass:
            # a global save without calling set_password will erase the password
            user.set_password(new_pass)
            user.save()
            self.save_m2m()
        else:
            user.save(update_fields=['username', 'first_name', 'last_name', 'email', 'is_superuser'])
            self.save_m2m()
        return user

          

class GroupForm(BaseForm):

    class Meta:
        model = Group
        fields = ('name',)
        widgets = {
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab('Info', 'name'),
            )
        )