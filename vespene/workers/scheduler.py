#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  scheduler.py - queues up periodically scheduled builds
#  --------------------------------------------------------------------------


from datetime import datetime, timedelta
from django.utils import timezone

from vespene.common.logger import Logger
from vespene.models.build import Build, QUEUED
from vespene.models.project import Project
from vespene.manager import jobkick
from datetime import datetime

LOG = Logger()

# =============================================================================

class Scheduler(object):

    def __init__(self):
        pass

    def schedulable_projects(self):
        return Project.objects.filter(
            schedule_enabled = True,
            active_build = None
        ).all()

    def day_of_week(self):
        return self.now.weekday()

    def day_of_week_name(self):
        day = self.day_of_week()
        names = [
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday'
        ]        
        return names[day]

    def schedule_is_enabled_for_today(self, project):
        name = self.day_of_week_name()
        return getattr(project, name)

    def has_queued_build(self, project):
        return Build.objects.filter(project=project, status=QUEUED).exists()

    def weekday_parameters(self, project):
        return (project.weekday_start_hours, project.weekday_start_minutes)

    def weekend_parameters(self, project):
        return (project.weekend_start_hours, project.weekend_start_minutes)

    def timing_parameters(self, project):
        day = self.day_of_week()
        if day < 6:
            return self.weekday_parameters(project)
        return self.weekend_parameters(project)

    def start_of_day(self):
        today = self.now.date()
        return datetime(today.year, today.month, today.day, tzinfo=timezone.utc) + timedelta(seconds=1)

    def split_string(self, data, mode=None):
        tokens = [ x for x in data.split(",") ]
        results = []
        if mode == 'hours':
            maximum = 24
        else:
            maximum = 60
        for val in tokens:
            x = val.strip()
            if '-' in x:
                (left, right) = x.split('-')
                left = int(left)
                right = int(right)
                if left < 0 or left > maximum or right < 0 or right > maximum or left > right:

                    return []
                for v in range(left, right+1):
                    results.append(v)
            else:
                x = int(x)
                if x < 0 or x > maximum:
                    return []
                results.append(x)
        return results
                

    def schedule_markers(self, project, parameters):
        """
        Schedule markers are the start points for all possible schedule events in the given day.
        They are input as a set of comma delimited hours and minutes and here we convert those
        to datetimes.
        """
        hours = parameters[0]
        minutes = parameters[1]
        day_start = self.start_of_day()
        # TODO: log about potentially invalid input
        # FIXME: try except logic around scheduler for bad inputs
        # FIXME: support ranges
        try:
            hours = self.split_string(hours, mode='hours')
            minutes = self.split_string(minutes, mode='minutes')
        except ValueError:
            return []
        results = []
        for h in hours:
            for m in minutes:
                time = day_start + timedelta(hours=h) + timedelta(minutes=m)
                results.append(time)
        return results

    def latest_schedule_marker_before_now(self, schedule_markers):
        """
        What is the latest possible schedule start time that MIGHT be launching this build
        if we find a build hasn't been launched after this time?
        """

        for marker in reversed(sorted(schedule_markers)):
            if marker < self.now:
                return marker
        return None

    def has_another_build_queued_after_marker(self, project, schedule_marker):
        """ 
        Has another build for this interval already been scheduled prior to 'now'?  If so, we won't
        be running the build. This includes running builds, not just builds in queued
        state.
        """
        builds = Build.objects.filter(
            project = project,
            queued_time__gt = schedule_marker
        )
        return builds.exists()

    def has_build_ran_too_recently(self, project):
        """
        A project can be configured to not run a scheduled build if a scheduled build
        has already been scheduled. This time can be no less than 1 minute to prevent
        double queuing.
        """
        last = project.last_build
        if last is None:
            return False
        threshold = project.schedule_threshold
        if not threshold:
            threshold = 1
        delta = self.now - last.queued_time
        minutes = delta.total_seconds() / 60.0
        return minutes < threshold

    def go(self):
        
        self.now = datetime.now(tz=timezone.utc)        
        projects = self.schedulable_projects()
        for project in projects:
            today = self.day_of_week()
            if self.has_queued_build(project):
                continue
            if not self.schedule_is_enabled_for_today(project):
                continue
            parameters = self.timing_parameters(project)
            schedule_markers = self.schedule_markers(project, parameters)
            schedule_marker = self.latest_schedule_marker_before_now(schedule_markers)
            if schedule_marker is None:
                continue
            if self.has_another_build_queued_after_marker(project, schedule_marker):
                continue
            if self.has_build_ran_too_recently(project):
                continue
            jobkick.start_project(project)

            
    