import mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest


from pylexa.app import (
    handle_launch_request,
    handle_session_ended_request,
    make_request_obj,
    route_request,
)
from pylexa.request import IntentRequest, LaunchRequest, SessionEndedRequest, Request


class TestMakeRequestObj(unittest.TestCase):

    def setUp(self):
        self.patcher = mock.patch('pylexa.app.flask_request')
        self.mocker = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def should_return_IntentRequest_when_intent(self):
        self.mocker.json = {
            'request': { 'type': 'IntentRequest' }
        }
        result = make_request_obj()
        self.assertIsInstance(result, IntentRequest)

    def should_return_LaunchRequest_when_launch(self):
        self.mocker.json = {
            'request': { 'type': 'LaunchRequest' }
        }
        result = make_request_obj()
        self.assertIsInstance(result, LaunchRequest)

    def should_return_SessionEndedRequest_when_session_ended(self):
        self.mocker.json = {
            'request': { 'type': 'SessionEndedRequest' }
        }
        result = make_request_obj()
        self.assertIsInstance(result, SessionEndedRequest)

    def should_return_Request_when_other_request(self):
        self.mocker.json = {
            'request': { 'type': 'SomethingElse' }
        }
        result = make_request_obj()
        self.assertIsInstance(result, Request)


class TestHandleLaunchRequestDecorator(unittest.TestCase):

    def setUp(self):
        self.patcher = mock.patch('pylexa.app.alexa_blueprint')
        self.blueprint_mock = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def should_set_launch_handler_on_blueprint(self):
        @handle_launch_request
        def my_handler(): pass

        self.assertEqual(self.blueprint_mock.launch_handler, my_handler)


class TestHandleSessionEndedRequestDecorator(unittest.TestCase):

    def setUp(self):
        self.patcher = mock.patch('pylexa.app.alexa_blueprint')
        self.blueprint_mock = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def should_set_session_ended_handler_on_blueprint(self):
        @handle_session_ended_request
        def my_handler(): pass

        self.assertEqual(self.blueprint_mock.session_ended_handler, my_handler)


class TestRouteRequest(unittest.TestCase):

    def setUp(self):
        self.make_request_obj_patcher = mock.patch('pylexa.app.make_request_obj')
        self.make_request_obj_mock = self.make_request_obj_patcher.start()
        self.request = mock.Mock(is_intent=False, is_launch=False, is_session_ended=False)
        self.make_request_obj_mock.return_value = self.request

        self.blueprint_patcher = mock.patch('pylexa.app.alexa_blueprint')
        self.blueprint_mock = self.blueprint_patcher.start()

        self.intents = {}
        self.intents_patcher = mock.patch('pylexa.app.intents', new=self.intents)
        self.intents_patcher.start()

    def tearDown(self):
        self.make_request_obj_patcher.stop()
        self.blueprint_patcher.stop()
        self.intents_patcher.stop()

    def should_call_launch_handler_for_launch_request(self):
        self.request.is_launch = True
        route_request()
        self.blueprint_mock.launch_handler.assert_called_once_with(self.request)

    def should_call_session_ended_handler_for_session_ended_request(self):
        self.request.is_session_ended = True
        route_request()
        self.blueprint_mock.session_ended_handler.assert_called_once_with(self.request)

    def should_call_intent_handler_for_recognized_intent(self):
        self.request.is_intent = True
        self.request.intent = 'foo'
        mock_intent_handler = mock.Mock()
        self.intents['foo'] = mock_intent_handler

        route_request()

        mock_intent_handler.assert_called_once_with(self.request)

    def should_call_uncrecognized_intent_handler_for_unrecognized_intent(self):
        self.request.is_intent = True
        self.request.intent = 'foo'
        mock_intent_handler = mock.Mock()
        self.intents['unrecognized_intent'] = mock_intent_handler

        route_request()

        mock_intent_handler.assert_called_once_with(self.request)

    def should_call_default_uncrecognized_intent_handler_when_no_custom_handler(self):
        self.request.is_intent = True
        self.request.intent = 'foo'

        with mock.patch('pylexa.app.default_unrecognized_intent_handler') as handler:
            route_request()
            handler.assert_called_once_with(self.request)

    def should_raise_exception_on_unknown_request_type(self):
        with self.assertRaises(Exception):
            route_request()
