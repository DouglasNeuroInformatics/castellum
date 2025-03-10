# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from collections import defaultdict

from simplecharts import StackedColumnRenderer

from castellum.recruitment.models.attributes import get_attribute_by_statistics_rank


def get_statistics(subjects, study):
    desc1 = get_attribute_by_statistics_rank('primary')
    if desc1:
        buckets1, get_bucket1 = desc1.field.get_statistics_grouping(study)
    else:
        return None

    desc2 = get_attribute_by_statistics_rank('secondary')
    if desc2:
        buckets2, get_bucket2 = desc2.field.get_statistics_grouping(study)
    else:
        buckets2, get_bucket2 = [(None, None)], lambda x: None

    statistics = defaultdict(lambda: defaultdict(lambda: 0))
    for subject in subjects:
        value1 = subject.attributes.get(desc1.json_key)
        key1 = get_bucket1(value1)

        if desc2:
            value2 = subject.attributes.get(desc2.json_key)
            key2 = get_bucket2(value2)
        else:
            key2 = None

        statistics[key1][key2] += 1

    data = {
        'rows': [{
            'label': str(label1),
            'values': [statistics[key1][key2] for key2, label2 in buckets2]
        } for key1, label1 in buckets1],
    }

    if len(buckets2) > 1:
        data['legend'] = []
        for key2, label2 in buckets2:
            count = sum(statistics[key1][key2] for key1, label1 in buckets1)
            data['legend'].append(f'{label2} ({count})')

    return data


def render_statistics(subjects, study):
    data = get_statistics(subjects, study)
    if not data:
        return None
    renderer = StackedColumnRenderer(width=760, height=320)
    return renderer.render(data)
