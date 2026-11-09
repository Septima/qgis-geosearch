"""QGIS' network stack against the mock Bifrost (what the Bifrost fetcher will use)."""

import json

import pytest
from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtCore import QByteArray, QSettings, QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

import bifrost_cases as bc
from conftest import MOCK_KEY, SETTINGS_GROUP


def post(url, body, key=MOCK_KEY, timeout_ms=None):
    req = QNetworkRequest(QUrl(url))
    req.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
    if key:
        req.setRawHeader(b"Authorization", ("Bearer " + key).encode())
    if timeout_ms:
        req.setTransferTimeout(timeout_ms)
    reply = QgsNetworkAccessManager.instance().blockingPost(
        req, QByteArray(json.dumps(body).encode())
    )
    status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
    content = bytes(reply.content()).decode("utf-8")
    # Qt 6 lowercases header names
    headers = {bytes(k).decode().lower(): bytes(reply.rawHeader(k)).decode() for k in reply.rawHeaderList()}
    return status, headers, json.loads(content) if content else None


def test_settings_point_at_the_mock(bifrost_mock):
    assert QSettings().value(SETTINGS_GROUP + "/bifrost_url") == bifrost_mock.url


def test_recorded_answer(bifrost_mock):
    fixture = bc.load_case_fixture("adr-vestergade-21-aar")
    ex = fixture["requests"][0]
    status, headers, response = post("%s/%s" % (bifrost_mock.url, ex["endpoint"]), ex["body"])
    assert status == 200
    assert headers["x-mock-fixture"] == "exact"
    assert response == ex["response"]
    assert bifrost_mock.request_log()[-1]["status"] == 200


def test_missing_key(bifrost_mock):
    status, _, response = post(bifrost_mock.url + "/search", {"input": "x"}, key=None)
    assert status == 401
    assert response["detail"] == "missing bearer credential"


def test_service_unavailable(bifrost_mock):
    bifrost_mock.configure(error="503", retry_after=5)
    status, headers, _ = post(bifrost_mock.url + "/search", {"input": "x"})
    assert status == 503
    assert headers["retry-after"] == "5"


def test_slow_answer_times_out(bifrost_mock):
    bifrost_mock.configure(error="slow", delay=2)
    status, _, _ = post(bifrost_mock.url + "/search", {"input": "x"}, timeout_ms=300)
    assert status is None
