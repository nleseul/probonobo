import time


class Action:
    def __init__(self, **kwargs):
        self.log = kwargs.get('log')
        self.delay = kwargs.get('delay')

    def perform(self, session):
        log = self._get_log()
        if log is not None:
            session.log(log)

        self._do_perform(session)

        delay = self._get_delay()
        if delay is not None and delay > 0:
            time.sleep(delay)

    def _get_log(self):
        return self.log

    def _get_delay(self):
        return self.delay

    def _do_perform(self, session):
        pass


class SuccessAction(Action):
    def _do_perform(self, session):
        session.complete_goal()


class FailureAction(Action):
    def _do_perform(self, session):
        session.fail_goal()


class AdvanceToGoalAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_goal = kwargs['next_goal']

    def _do_perform(self, session):
        session.set_goal(self.next_goal)


class SelectAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coords = kwargs['coords']

    def _do_perform(self, session):
        session.device.select_at_coord(self.coords)


class DragAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start = kwargs['start']
        self.end = kwargs['end']
        self.duration = kwargs.get('duration')

        if self.duration is None:
            self.duration = 1

    def _do_perform(self, session):
        session.device.drag(self.start, self.end, self.duration)


class KeyPressAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.key = kwargs['key']

    def _do_perform(self, session):
        session.device.press_key(self.key)