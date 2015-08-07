# cabot-alert-slack

A simple [Cabot] alerting plugin for [Slack].  It's intended as a general
"alert log" and not as a primary source for on-call alerts, and as such it
doesn't do anything with the duty roster or subscriptions.

## installation

```
# add the plugin to the list of enabled plugins
CABOT_PLUGINS_ENABLED=...,cabot_alert_slack==1.0

SLACK_WEBHOOK_URL=https://...
SLACK_ALERT_CHANNEL="#monitoring"
```

[Cabot]: https://github.com/arachnys/cabot
[Slack]: https://slack.com/
