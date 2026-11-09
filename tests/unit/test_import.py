import subprocess
import sys
import textwrap


def test_core_imports_without_qgis_or_qt():
    # A fresh interpreter, so modules imported by other tests cannot hide an import.
    code = textwrap.dedent(
        """
        import sys
        import geosearch_dk.bifrost
        import geosearch_dk.bifrost.core, geosearch_dk.bifrost.display
        import geosearch_dk.bifrost.kommunefilter, geosearch_dk.bifrost.types
        import geosearch_dk.bifrost.transport, geosearch_dk.bifrost.settings_model
        import geosearch_dk.kommunefilter_info
        bad = sorted(m for m in sys.modules if m.split(".")[0] in ("qgis", "PyQt5", "PyQt6", "sip"))
        assert not bad, bad
        """
    )
    subprocess.run([sys.executable, "-c", code], check=True, env=_env())


def _env():
    import os

    import geosearch_dk

    src = os.path.dirname(os.path.dirname(geosearch_dk.__file__))
    env = dict(os.environ)
    env["PYTHONPATH"] = src
    return env
