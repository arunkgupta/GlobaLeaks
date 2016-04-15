# -*- coding: utf-8 -*-
from twisted.internet.defer import inlineCallbacks

from globaleaks import anomaly
from globaleaks.tests import helpers

from globaleaks.jobs import statistics_sched

# E non è la distanza ad abitare l'assenza.
# https://www.youtube.com/watch?v=UBdlNlDZDZA

# FIXME
# currently the following unit tests does not really perform complete
# unit tests and check but simply trigger the schedulers in order to
# raise the code coverage


class TestAnomaliesSchedule(helpers.TestGL):
    @inlineCallbacks
    def test_anomalies_schedule(self):
        self.n = 0

        full_ammo = 1000000

        original_get_disk_anomaly_conditions = anomaly.get_disk_anomaly_conditions

        conditions_count = len(original_get_disk_anomaly_conditions(full_ammo,
                                                                    full_ammo,
                                                                    full_ammo,
                                                                    full_ammo))

        def mock_get_disk_anomaly_conditions(*args, **kwargs):
            conditions = original_get_disk_anomaly_conditions(*args, **kwargs)
            # activate one condition at once
            for i in range(len(conditions)):
                conditions[i]['condition'] = (i == self.n)

            return conditions

        anomaly.get_disk_anomaly_conditions = mock_get_disk_anomaly_conditions

        # testing the scheduler with all the conditions unmet
        self.n = -1
        yield statistics_sched.AnomaliesSchedule().operation()

        # testing the scheduler enabling all conditions one at once
        for j in range(conditions_count):
            self.n = j
            yield statistics_sched.AnomaliesSchedule().operation()

        yield statistics_sched.AnomaliesSchedule().operation()

        # testing the scheduler with all the conditions unmet
        # a second time in order test the accept_submissions value
        self.n = -1
        yield statistics_sched.AnomaliesSchedule().operation()


class TestStaticsSchedule(helpers.TestGL):
    @inlineCallbacks
    def test_statistics_schedule(self):
        yield statistics_sched.StatisticsSchedule().operation()
