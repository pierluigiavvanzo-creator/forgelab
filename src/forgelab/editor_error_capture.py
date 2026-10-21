"""Private child-process observer for the pinned Aider provider boundary.

Copied as sitecustomize.py into tool-home, never into the editable workspace.
No output parsing, provider calls, retry changes, or completion logging.
"""
import functools
import importlib.abc
import importlib.machinery
import json
import os
from pathlib import Path
import sys


def _append(event):
    with Path(os.environ["FORGELAB_EDITOR_ERRORS"]).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")


def _observe(send):
    @functools.wraps(send)
    def observed(*args, **kwargs):
        try:
            return send(*args, **kwargs)
        except Exception as error:
            # Only provider exceptions, not local validation or generated code.
            if type(error).__module__.split(".")[0] in {"litellm", "httpx", "openai"}:
                chain, seen = [], set()
                current = error
                while current is not None and id(current) not in seen:
                    seen.add(id(current))
                    chain.append({
                        "type": type(current).__name__,
                        "message": str(current),
                        "status_code": getattr(current, "status_code", None),
                    })
                    current = current.__cause__ or current.__context__
                _append({"event": "provider_error", "exceptions": chain})
            raise
    return observed


class _ModelsLoader(importlib.abc.Loader):
    def __init__(self, original):
        self.original = original

    def create_module(self, spec):
        return self.original.create_module(spec)

    def exec_module(self, module):
        self.original.exec_module(module)
        module.Model.send_completion = _observe(module.Model.send_completion)
        _append({"event": "provider_observer_attached"})


class _ModelsFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname != "aider.models":
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is not None and spec.loader is not None:
            spec.loader = _ModelsLoader(spec.loader)
        return spec


if __name__ == "sitecustomize":
    sys.meta_path.insert(0, _ModelsFinder())
    _append({"event": "observer_ready"})
