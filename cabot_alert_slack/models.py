import json
import os

import requests

from cabot.cabotapp.alert import AlertPlugin
from django.conf import settings
from django.template import Template, Context


TEXT_TEMPLATE = "<{{ scheme }}://{{ host }}{% url 'service' pk=service.id %}|{{ service.name }}> {{ message }}"
URL_TEMPLATE = "{{ scheme }}://{{ host }}{% url 'result' pk=check.last_result.id %}"
MESSAGES_BY_STATUS = {
    "PASSING": "has returned to normal! :up:",
    "WARNING": "is reporting WARNING. :warning:",
    "ERROR": "is reporting ERROR. :negative_squared_cross_mark:",
    "CRITICAL": "is reporting CRITICAL errors! :skull::sos:",
}


class SlackAlert(AlertPlugin):
    name = "Slack"
    author = "Neil Williams"

    def send_alert(self, service, users, duty_officers):
        self._send_alert(service, acked=False)

    def send_alert_update(self, service, users, duty_officers):
        self._send_alert(service, acked=True)

    def _send_alert(self, service, acked):
        overall_status = service.overall_status
        if not (acked and overall_status != "PASSING"):
            message = MESSAGES_BY_STATUS[overall_status]
        else:
            user = service.unexpired_acknowledgement().user
            name = user.first_name or user.username
            message = "is being worked on by {}. :hammer:".format(name)

        context = Context({
            "scheme": settings.WWW_SCHEME,
            "host": settings.WWW_HTTP_HOST,
            "service": service,
            "message": message,
        })
        text = Template(TEXT_TEMPLATE).render(context)

        attachments = []
        for check in service.all_failing_checks():
            if check.importance == "WARNING":
                color = "warning"
            else:
                color = "danger"

            check_context = Context({
                "scheme": settings.WWW_SCHEME,
                "host": settings.WWW_HTTP_HOST,
                "check": check,
            })
            url = Template(URL_TEMPLATE).render(check_context)

            attachment = {
                "fallback": "{}: {}: {}".format(check.name, check.importance, url),
                "title": check.name,
                "title_link": url,
                "text": check.last_result().error,
                "color": color,
            }
            attachments.append(attachment)

        self._send_slack_webhook(text, attachments)

    def _send_slack_webhook(self, text, attachments):
        url = os.environ["SLACK_WEBHOOK_URL"]
        channel = os.environ["SLACK_ALERT_CHANNEL"]

        response = requests.post(url, data=json.dumps({
            "username": "Cabot",
            "icon_emoji": ":dog2:",
            "channel": channel,
            "text": text,
            "attachments": attachments,
        }))
        response.raise_for_status()
