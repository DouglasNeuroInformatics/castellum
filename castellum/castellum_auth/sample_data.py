# (c) 2018
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
#
# This file is part of Castellum.
#
# Castellum is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Castellum is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Castellum. If not, see
# <http://www.gnu.org/licenses/>.

# NOTE: permissions are identified only by their codename, without app_label.
# This is unique right now, but that can change in the future.
GROUPS = {
    'Study coordinator': [
        'add_study',
        'view_study',
        'change_study',
        'delete_study',
        'add_subjectfilter',
        'view_subjectfilter',
        'change_subjectfilter',
        'delete_subjectfilter',
    ],
    'Subject manager': [
        'view_subject',
        'change_subject',
        'add_contact',
        'view_contact',
        'change_contact',
        'delete_contact',
        'add_attributeset',
        'view_attributeset',
        'change_attributeset',
        'delete_attributeset',
    ],
    'Recruiter': [
        'view_contact',
        'add_participationrequest',
        'view_participationrequest',
        'change_participationrequest',
        'delete_participationrequest',
    ],
}

USERS = {
    'Andreas': [],
    'Emma': ['Recruiter'],

    # first testing group
    'Vera': ['Study coordinator'],
    'Arne': ['Subject manager'],
    'Edwin': ['Subject manager', 'Recruiter'],

    # second testing group
    'Anna': ['Study coordinator'],
    'Max': ['Subject manager'],
    'Sonja': ['Subject manager', 'Recruiter'],

    # third testing group
    'Claus': ['Study coordinator'],
    'Flora': ['Subject manager'],
    'Oskar': ['Subject manager', 'Recruiter'],

    # fourth testing group
    'Hans': ['Study coordinator'],
    'Nina': ['Subject manager'],
    'Pia': ['Subject manager', 'Recruiter'],
}
