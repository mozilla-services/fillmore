# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Utility functions for setting up Sentry."""

import logging
from typing import Any, Callable, List
from urllib.parse import urlparse

import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger

from francis import SCRUBBER_MODULE_NAME


logger = logging.getLogger(__name__)


def get_sentry_base_url(sentry_dsn: str) -> str:
    """Given a sentry_dsn, returns the base url

    This is helpful for tests that need the url to the fakesentry api.

    :arg sentry_dsn: the sentry base url

    """
    if not sentry_dsn:
        raise Exception("sentry_dsn required")

    parsed_dsn = urlparse(sentry_dsn)
    netloc = parsed_dsn.netloc
    if "@" in netloc:
        netloc = netloc[netloc.find("@") + 1 :]

    return f"{parsed_dsn.scheme}://{netloc}/"


def set_up_sentry(
    release: str,
    host_id: str,
    sentry_dsn: str,
    integrations: List[Any] = None,
    before_send: Callable = None,
    **kwargs: Any,
) -> None:
    """Set up Sentry

    By default, this will set up default integrations
    (https://docs.sentry.io/platforms/python/configuration/integrations/default-integrations/),
    but not the auto-enabling ones.

    :arg release: the release name to tag events with
    :arg host_id: some str representing the host this service is running on
    :arg sentry_dsn: the Sentry DSN
    :arg integrations: list of sentry integrations to set up;
    :arg before_send: set this to a callable to handle the Sentry before_send hook

        For scrubbing, do something like this::

            scrubber = Scrubbing(scrub_keys=SCRUB_RULES_DEFAULT + my_scrub_rules)

        and then pass that as the ``before_send`` value.

    :arg kwargs: any additional arguments to pass to sentry_sdk.init()

    """
    if not sentry_dsn:
        return

    sentry_sdk.init(
        dsn=sentry_dsn,
        release=release,
        send_default_pii=False,
        server_name=host_id,
        # This prevents Sentry from trying to enable all the auto-enabling
        # integrations. We only want the ones we explicitly set up. This
        # provents sentry from loading the Falcon integration (which fails) in a Django
        # context.
        auto_enabling_integrations=False,
        integrations=integrations or [],
        before_send=before_send or None,
        **kwargs,
    )

    # Ignore logging from this module
    ignore_logger(SCRUBBER_MODULE_NAME)
