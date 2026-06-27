import os
from types import SimpleNamespace
from uuid import uuid4

try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - local fallback for dev/test without celery installed
    class _FallbackTask:
        def __init__(self, fn):
            self._fn = fn

        def __call__(self, *args, **kwargs):
            return self._fn(*args, **kwargs)

        def delay(self, *args, **kwargs):
            task_id = str(uuid4())
            task_context = SimpleNamespace(request=SimpleNamespace(id=task_id))
            self._fn(task_context, *args, **kwargs)
            return SimpleNamespace(id=task_id)

    class Celery:  # type: ignore[override]
        def __init__(self, *args, **kwargs):
            self.conf = SimpleNamespace(task_routes={})

        def task(self, *args, **kwargs):
            def decorator(fn):
                return _FallbackTask(fn)

            return decorator


broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/1')
task_always_eager = os.getenv('CELERY_TASK_ALWAYS_EAGER', '').lower() in {'1', 'true', 'yes', 'on'}

celery_app = Celery('lightscan', broker=broker_url, backend=result_backend)
celery_app.conf.task_always_eager = task_always_eager
celery_app.conf.task_eager_propagates = True
celery_app.conf.task_routes = {'app.workers.jobs.run_discovery_task_payload': {'queue': 'discovery'}}
