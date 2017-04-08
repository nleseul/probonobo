

class SessionLostException(Exception):
    pass


class GoalFailedException(Exception):
    pass


class Session:

    is_active = False

    def __init__(self, **kwargs):
        self.device = kwargs['device']
        self.goals = kwargs.get('goals')
        self.identifiers = kwargs.get('identifiers')

        self.current_goal = None

    def begin(self):
        self.device.connect()
        self.is_active = True

    def end(self):
        self.device.disconnect()
        self.is_active = False

    def run(self):
        timeout = 0
        last_location = None
        while self.current_goal is not None:
            goal_data = self.goals[self.current_goal]
            screenshot = self.device.get_screenshot()
            matched_location = None
            for location, location_actions in goal_data['actions'].items():
                if self.does_screen_match(location, screenshot):
                    self.perform_actions(location_actions)
                    matched_location = location
                    break
            else:
                self.perform_actions(goal_data['default_actions'])
            if matched_location == last_location:
                timeout += 1
                if timeout > goal_data['timeout_counter']:
                    raise SessionLostException('Lost during goal ' + self.current_goal + '!')

            last_location = matched_location

    def complete_goal(self):
        self.current_goal = None

    def fail_goal(self):
        raise GoalFailedException('Failed to complete goal ' + self.current_goal + '!')

    def perform_actions(self, actions):
        for action in actions:
            action.perform(self)

    def does_screen_match(self, screen_id, screenshot=None):
        if screenshot is None:
            screenshot = self.device.get_screenshot()
        identifier = self.identifiers[screen_id]
        return identifier(screenshot=screenshot)

    def identify_screen(self, screenshot=None):
        if screenshot is None:
            screenshot = self.device.get_screenshot()
        for screen_id, identifier in self.identifiers.items():
            if identifier(screenshot=screenshot):
                return screen_id
        return None

    def set_goal(self, goal):
        self.current_goal = goal

    def log(self, message='', **kwargs):
        print(message, **kwargs)
