.. image:: vespene_logo.png
   :alt: Vespene Logo
   :align: right

.. _webhooks:

********
Webhooks
********

Using webhooks, a source control system can trigger Vespene builds automatically when new code is pushed.

Configuration in the Source Control Product
-------------------------------------------

Webhooks must be configured in your source control system, and you should consult their documentation for how to set this up.

Webhooks should point to http://your-vespene-server.example.com/webhooks

The URL you provide to something that generates webhooks will not change project by project.  Vespene looks at the payload of the webhook to find out what repo the event is "about"
and then matches up the repositories mentioned with your project.

Here are two very important things to consider:

* to avoid extra builds being triggered by extraneous events, only PUSH webhooks should be sent
* all webhooks should be configured to send JSON

Vespene has been tested with GitHub and support for GitLab *should* work at this time. For some source control systems, Vespene may need a VERY 
minor set of code additions to be able to support it. We welcome ALL of these additions and can work with you to get these added in ASAP if you send
us a link to the webhook documentation.

Configuration in Vespene
------------------------

For each project that should respond to a webhook with a new build, the enable webhook checkbox must be checked no the project.
This checkbox is OFF by default, so no one can just configure up a webhook externally and start making Vespene fire off builds.

Additionally, there is an optional field, 'webhook_token'.  Normally this is blank, but this provides as a *BASIC* but generic
extra safeguard. If supplied, the token must match the query string of the webhook.

For instance, if the token is set to "badwolf", the URL for that project would have to be http://your-vespene-server.example.com/webhooks?token=badwolf -- you would use
that URL instead of the generic webhook URL when setting the webhook up in git. If the webhook token doesn't match, the webhook will not fire.

The webhook token can be unique per project.

Network Relays
--------------

Often a Vespene server on a private network will want to recieve webhooks from a hosted source control management service.

There are commercial solutions for this (I have tested webhook-relay.com and it works great), though you could also write a POST forwarder yourself if you have any internet-facing web application.  You would then only accept
connections from your source control management system for the webhook URL, for example, the public IPs from github.

Testing
-------

Push to your repository and see if a build was triggered.

See the logs/output from Vespene if needed for debug information.


