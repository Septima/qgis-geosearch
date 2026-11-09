"""Sends ``BifrostRequest``s with ``QgsNetworkAccessManager``.

Requests go through QGIS' network manager, so proxy settings apply and they
show up in the QGIS network logger. Everything that does not need Qt is in
``transport``.

Works with Qt5 (QGIS 3) and Qt6 (QGIS 4).
"""

from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtCore import QObject, QTimer, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest

from . import transport
from .translation import tr
from .transport import (
    BifrostMissingKey,
    BifrostNetworkError,
    BifrostNotAuthorized,
    SEARCH_TIMEOUT_MS,
)

try:
    from qgis.core import QgsSetRequestInitiatorClass
except ImportError:  # pragma: no cover
    QgsSetRequestInitiatorClass = None


class BifrostCall(QObject):
    """The replies of one ``BifrostClient.send``. Abort with ``abort()``."""

    def __init__(self, client, requests, callback, timeout_ms):
        QObject.__init__(self, client)
        self._client = client
        self._requests = list(requests)
        self._callback = callback
        self._timeout_ms = timeout_ms
        self._results = [None] * len(self._requests)
        self._pending = len(self._requests)
        self._replies = {}
        self._retries = [0] * len(self._requests)
        self.aborted = False
        self.done = False

    def start(self):
        if not self._requests:
            QTimer.singleShot(0, self._finish)
            return
        for i in range(len(self._requests)):
            self._send(i)

    def abort(self):
        """Stop all replies. The callback is not called."""
        if self.done or self.aborted:
            return
        self.aborted = True
        for reply, timer in list(self._replies.values()):
            timer.stop()
            reply.abort()
        self._replies.clear()
        self._client._forget(self)

    def _send(self, i):
        if self.aborted:
            return
        req = self._requests[i]
        key = self._client.key()
        if not key:
            # Async, so the callback never runs inside send().
            QTimer.singleShot(0, lambda i=i: self._set_result(i, BifrostMissingKey()))
            return
        url = transport.endpoint_url(self._client.base_url(), req.endpoint)
        request = QNetworkRequest(QUrl(url))
        for name, value in transport.request_headers(key).items():
            request.setRawHeader(name.encode("ascii"), value.encode("utf-8"))
        if QgsSetRequestInitiatorClass is not None:
            QgsSetRequestInitiatorClass(request, "GeosearchDK")
        reply = self._client.network_manager.post(
            request, transport.encode_body(req.body)
        )
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda r=reply: self._on_timeout(r))
        timer.start(self._timeout_ms)
        self._replies[i] = (reply, timer)
        reply.setProperty("geosearch_timed_out", False)
        reply.finished.connect(lambda i=i, r=reply: self._on_finished(i, r))

    def _on_timeout(self, reply):
        reply.setProperty("geosearch_timed_out", True)
        reply.abort()

    def _on_finished(self, i, reply):
        entry = self._replies.pop(i, None)
        if self.aborted or entry is None or entry[0] is not reply:
            # abort() emits finished synchronously; nothing to read then.
            reply.deleteLater()
            return
        entry[1].stop()
        entry[1].deleteLater()
        try:
            result = self._decode(reply)
        finally:
            reply.deleteLater()
        delay = transport.retry_delay(result, self._retries[i])
        if delay is not None:
            self._retries[i] += 1
            QTimer.singleShot(int(delay * 1000), lambda i=i: self._send(i))
            return
        if isinstance(result, BifrostNotAuthorized):
            self._client.not_authorized.emit()
        self._set_result(i, result)

    def _decode(self, reply):
        if reply.property("geosearch_timed_out"):
            return BifrostNetworkError(
                tr("bifrost", "Bifrost svarede ikke inden for %d sekunder")
                % (self._timeout_ms // 1000)
            )
        status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        body = bytes(reply.readAll())
        if status is None:
            if reply.error() == QNetworkReply.NetworkError.NoError:
                status = 200
            else:
                return BifrostNetworkError(
                    tr("bifrost", "Kunne ikke kontakte Bifrost: %s") % reply.errorString()
                )
        retry_after = None
        if reply.hasRawHeader(b"Retry-After"):
            retry_after = bytes(reply.rawHeader(b"Retry-After"))
        try:
            return transport.decode_response(status, body, retry_after)
        except Exception as e:
            return e

    def _set_result(self, i, result):
        self._results[i] = result
        self._pending -= 1
        if self._pending == 0:
            self._finish()

    def _finish(self):
        if self.aborted or self.done:
            return
        self.done = True
        self._client._forget(self)
        self._callback(self._results)


class BifrostClient(QObject):
    """Posts Bifrost requests in parallel.

    ``base_url`` and ``key`` are callables, so changed settings apply to the
    next request. ``send(requests, callback)`` calls ``callback(responses)``
    once, where ``responses[i]`` is the decoded JSON of ``requests[i]`` or the
    ``BifrostError`` it failed with (the shape ``core.collect_rows`` takes).
    """

    not_authorized = pyqtSignal()

    def __init__(self, base_url, key, network_manager=None, parent=None):
        QObject.__init__(self, parent)
        self._base_url = base_url
        self._key = key
        self.network_manager = network_manager or QgsNetworkAccessManager.instance()
        self._calls = set()

    def base_url(self):
        return self._base_url()

    def key(self):
        return self._key()

    def send(self, requests, callback, timeout_ms=SEARCH_TIMEOUT_MS):
        call = BifrostCall(self, requests, callback, timeout_ms)
        self._calls.add(call)
        call.start()
        return call

    def abort_all(self):
        for call in list(self._calls):
            call.abort()

    def _forget(self, call):
        self._calls.discard(call)
        call.deleteLater()
