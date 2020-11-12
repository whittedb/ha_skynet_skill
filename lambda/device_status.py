# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import typing
from datetime import datetime
import logging.config
import json
from ask_sdk_core.dispatch_components import AbstractRequestHandler
import ask_sdk_core.utils as ask_utils
from ask_sdk_model import Response
from ask_sdk_model.dialog import DelegateDirective
import pynamodb.models
from models import AwsTellMeTable

if typing.TYPE_CHECKING:
    from ask_sdk_core.handler_input import HandlerInput
    from ask_sdk_model.simple_slot_value import SimpleSlotValue

logger = logging.getLogger(__name__)


class DeviceStatusIntentHandler(AbstractRequestHandler):
    """Handler for Device Status Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("DeviceStatusIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.debug("Progress: {}".format(ask_utils.get_dialog_state(handler_input)))
        docs = AwsTellMeTable.scan()
        locations = []
        sensors = []
        for doc in docs:
            location = doc.location.lower()
            if location not in locations:
                locations.append(location)
            location = doc.location.replace(" ", "").replace(".", "").lower()
            if location not in locations:
                locations.append(location)
            sensor = doc.sensor_type.lower()
            if sensor not in sensors:
                sensors.append(sensor)
            sensor = doc.sensor_type.replace(" ", "").replace(".", "").lower()
            if sensor not in sensors:
                sensors.append(sensor)

        location, sensor = self.get_location_sensor(handler_input)
        logger.debug(location)
        logger.debug(sensor)
        if location is None:
            speak_output = "A location must be specified"
            return (handler_input.response_builder
                    .set_should_end_session(False)
                    .speak(speak_output)
                    .add_directive(DelegateDirective(handler_input.request_envelope.request.intent))
                    .ask("Which room?")
                    .response
                    )
        elif location.get("id", location.get("name", location["spoken"])) not in locations:
            speak_output = "{} is not a valid location".format(location["spoken"])
            ask_utils.get_slot(handler_input, "location").value = None
            return (handler_input.response_builder
                    .set_should_end_session(False)
                    .speak(speak_output)
                    .add_directive(DelegateDirective(handler_input.request_envelope.request.intent))
                    .ask("Which room?")
                    .response
                    )
        elif sensor is None:
            speak_output = "A sensor type must be specified"
            ask_utils.get_slot(handler_input, "sensor").value = None
            return (handler_input.response_builder
                    .set_should_end_session(False)
                    .speak(speak_output)
                    .add_directive(DelegateDirective(handler_input.request_envelope.request.intent))
                    .ask("Which sensor?")
                    .response
                    )
        elif sensor.get("id", sensor.get("name", location["spoken"])) not in sensors:
            speak_output = "{} is not a valid sensor".format(sensor["spoken"])
            ask_utils.get_slot(handler_input, "sensor").value = None
            return (handler_input.response_builder
                    .set_should_end_session(False)
                    .speak(speak_output)
                    .add_directive(DelegateDirective(handler_input.request_envelope.request.intent))
                    .ask("Which sensor?")
                    .response
                    )
        else:
            loc_id = self.make_db_id_from_resolution(location)
            sensor_id = self.make_db_id_from_resolution(sensor)
            db_id = "{}{}".format(loc_id, sensor_id)
            try:
                doc = AwsTellMeTable.get(db_id)
                last_reading_time = datetime(doc.year, doc.month, doc.day,
                                             doc.hour, doc.minute, doc.second, doc.microsecond)
                now = datetime.now()
                last_reading_delta = now - last_reading_time
                speak_output = "{}".format(doc.value)
                if doc.unit:
                    speak_output = speak_output + " {}".format(doc.unit)
                if last_reading_delta.days == 1:
                    speak_output = speak_output + " as of yesterday"
                elif last_reading_delta.days > 1:
                    speak_output = speak_output + " on {}".format(last_reading_time.strftime("%B %d, %Y at %I:%M %p"))
            except pynamodb.models.DoesNotExist:
                speak_output = "{} {} does not exist.".format(location["spoken"], sensor["spoken"])

        return (handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
                )

    @staticmethod
    def get_location_sensor(handler_input):
        # type: (HandlerInput) -> (str, str)

        slot_values = ask_utils.get_simple_slot_values(ask_utils.get_slot_value_v2(handler_input, "location"))
        if slot_values:
            location = DeviceStatusIntentHandler.get_slot_resolution(slot_values[0])
        else:
            location = None

        slot_values = ask_utils.get_simple_slot_values(ask_utils.get_slot_value_v2(handler_input, "sensor"))
        if slot_values:
            sensor = DeviceStatusIntentHandler.get_slot_resolution(slot_values[0])
        else:
            sensor = None

        return location, sensor

    @staticmethod
    def get_slot_resolution(slot_value):
        # type: (SimpleSlotValue) -> dict

        rv = None
        if slot_value.resolutions:
            rv = {}
            rv.update({"spoken": slot_value.value.lower()})
            try:
                slot_value_id = slot_value.resolutions.resolutions_per_authority[0].values[0].value.id.lower()
                rv.update({"id": slot_value_id.lower()})
            except (AttributeError, TypeError):
                pass
            try:
                name = slot_value.resolutions.resolutions_per_authority[0].values[0].value.name.lower()
                rv.update({"name": name.lower()})
            except (AttributeError, TypeError):
                pass

        return rv

    def make_db_id_from_resolution(self, resolution):
        # type: (dict) -> str
        return resolution.get("id", resolution.get("name", resolution["spoken"]))\
            .replace(" ", "").replace(".", "").lower()

    @staticmethod
    def get_attributes(handler_input):
        # type: (HandlerInput) -> (dict, dict)
        return handler_input.attributes_manager.session_attributes, handler_input.attributes_manager.request_attributes
