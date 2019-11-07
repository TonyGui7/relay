import datetime
import time

import requests

session = requests.session()


class SentryLike(object):
    _healthcheck_passed = False

    dsn_public_key = "31a5a894b4524f74a9a8d0e27e21ba91"

    @property
    def url(self):
        return "http://{}:{}".format(*self.server_address)

    def _wait(self, path):
        backoff = 0.1
        while True:
            try:
                self.get(path).raise_for_status()
                break
            except Exception:
                time.sleep(backoff)
                if backoff > 10:
                    raise
                backoff *= 2

    def wait_relay_healthcheck(self):
        if self._healthcheck_passed:
            return

        self._wait("/api/relay/healthcheck/")
        self._healthcheck_passed = True

    def __repr__(self):
        return "<{}({})>".format(self.__class__.__name__, repr(self.upstream))

    @property
    def dsn(self):
        """DSN for which you will find the events in self.captured_events"""
        # bogus, we never check the DSN
        return "http://{}@{}:{}/42".format(self.dsn_public_key, *self.server_address)

    def iter_public_keys(self):
        try:
            yield self.public_key
        except AttributeError:
            pass

        if self.upstream is not None:
            if isinstance(self.upstream, tuple):
                for upstream in self.upstream:
                    yield from upstream.iter_public_keys()
            else:
                yield from self.upstream.iter_public_keys()

    def basic_project_config(self):
        return {
            "publicKeys": [
                {
                    "publicKey": self.dsn_public_key,
                    "isEnabled": True,
                    "numericId": 123,
                    "quotas": [],
                }
            ],
            "rev": "5ceaea8c919811e8ae7daae9fe877901",
            "disabled": False,
            "lastFetch": datetime.datetime.utcnow().isoformat() + "Z",
            "lastChange": datetime.datetime.utcnow().isoformat() + "Z",
            "config": {
                "allowedDomains": ["*"],
                "trustedRelays": list(self.iter_public_keys()),
                "piiConfig": {
                    "rules": {},
                    "applications": {
                        "$string": ["@email", "@mac", "@creditcard", "@userpath"],
                        "$object": ["@password"],
                    },
                },
            },
            "slug": "python",
        }

    def full_project_config(self):
        basic = self.basic_project_config()
        full = {
            "organizationId": 1,
            "config": {
                "excludeFields": [],
                "filterSettings": {
                    "browser-extensions": {"isEnabled": True},
                    "web-crawlers": {"isEnabled": True},
                    "localhost": {"isEnabled": False},
                    "legacy-browsers": {"isEnabled": True, "options": ["ie_pre_9"]},
                },
                "scrubIpAddresses": False,
                "sensitiveFields": [],
                "scrubDefaults": True,
                "scrubData": True,
                "groupingConfig": {
                    "id": "legacy:2019-03-12",
                    "enhancements": "eJybzDhxY05qemJypZWRgaGlroGxrqHRBABbEwcC",
                },
                "blacklistedIps": ["127.43.33.22"],
                "trustedRelays": [],
            },
        }

        return {
            **basic,
            **full,
            "config": {**basic["config"], **full["config"]},
        }

    def send_event(self, project_id, payload=None):
        if payload is None:
            payload = {"message": "Hello, World!"}

        if isinstance(payload, dict):
            kwargs = {"json": payload}
        elif isinstance(payload, bytes):
            kwargs = {"data": payload}
        else:
            raise ValueError(f"Invalid type {type(payload)} for payload.")

        response = self.post(
            "/api/%s/store/" % project_id,
            headers={
                "Content-Type": "application/octet-stream",
                "X-Sentry-Auth": (
                    "Sentry sentry_version=5, sentry_timestamp=1535376240291, "
                    "sentry_client=raven-node/2.6.3, "
                    "sentry_key={}".format(self.dsn_public_key)
                ),
            },
            **kwargs,
        )
        response.raise_for_status()

    def send_security_report(
        self, project_id, content_type, payload, release, environment
    ):
        response = self.post(
            "/api/{}/security/?sentry_key={}&sentry_release={}&sentry_environment={}".format(
                project_id, self.dsn_public_key, release, environment
            ),
            headers={
                "Content-Type": content_type,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            },
            json=payload,
        )
        response.raise_for_status()

    def request(self, method, path, **kwargs):
        assert path.startswith("/")
        return session.request(method, self.url + path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("post", path, **kwargs)

    def get(self, path, **kwargs):
        return self.request("get", path, **kwargs)