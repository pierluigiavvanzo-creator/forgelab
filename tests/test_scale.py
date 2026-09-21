import tempfile
import threading
import time
import unittest
from pathlib import Path

from forgelab.scale import DurableTaskQueue, TenantResultCache, UsageMeter, run_parallel_dag


class ScaleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)

    def tearDown(self): self.tmp.cleanup()

    def test_queue_is_idempotent_and_tenant_isolated(self):
        q=DurableTaskQueue(self.root/"queue.db")
        self.assertTrue(q.enqueue("a","t1",{"x":1},idempotency_key="same"))
        self.assertFalse(q.enqueue("a","t2",{"x":2},idempotency_key="same"))
        self.assertTrue(q.enqueue("b","t1",{"x":3},idempotency_key="same"))
        self.assertEqual(q.lease("a","w")["payload"],{"x":1})
        self.assertIsNone(q.lease("a","w2"))
        self.assertEqual(q.lease("b","w")["payload"],{"x":3})

    def test_queue_retry_becomes_dead_at_cap(self):
        q=DurableTaskQueue(self.root/"queue.db"); q.enqueue("a","t",{},max_attempts=2)
        q.lease("a","w"); self.assertEqual(q.fail("a","t","w","first"),"queued")
        q.lease("a","w"); self.assertEqual(q.fail("a","t","w","second"),"dead")
        self.assertEqual(q.counts("a"),{"dead":1})

    def test_queue_rejects_wrong_worker_completion(self):
        q=DurableTaskQueue(self.root/"queue.db"); q.enqueue("a","t",{}); q.lease("a","w")
        with self.assertRaisesRegex(ValueError,"not leased"): q.complete("a","t","other")

    def test_cache_is_canonical_and_tenant_isolated(self):
        c=TenantResultCache(self.root/"cache.db")
        self.assertEqual(c.key("test",{"b":2,"a":1}),c.key("test",{"a":1,"b":2}))
        key=c.key("test",{"a":1}); c.put("a",key,{"ok":True})
        self.assertEqual(c.get("a",key),{"ok":True}); self.assertIsNone(c.get("b",key))

    def test_parallel_dag_runs_ready_layer_concurrently(self):
        tasks=[{"task_id":"a","dependencies":[]},{"task_id":"b","dependencies":[]},{"task_id":"c","dependencies":["a","b"]}]
        lock=threading.Lock(); active=0; peak=0
        def execute(task):
            nonlocal active,peak
            with lock: active+=1; peak=max(peak,active)
            time.sleep(.03)
            with lock: active-=1
            return task["task_id"]
        results=run_parallel_dag(tasks,execute,max_workers=2)
        self.assertEqual([r.status for r in results],["passed"]*3); self.assertEqual(peak,2)

    def test_parallel_dag_blocks_descendant_after_failure(self):
        tasks=[{"task_id":"a","dependencies":[]},{"task_id":"b","dependencies":["a"]}]
        def execute(task):
            if task["task_id"]=="a": raise RuntimeError("boom")
        results=run_parallel_dag(tasks,execute)
        self.assertEqual([r.status for r in results],["failed","blocked"])

    def test_usage_meter_enforces_cap_and_tenant_boundary(self):
        m=UsageMeter(self.root/"usage.db"); m.record("a","run","tokens",100,0.4,cost_cap=1)
        with self.assertRaisesRegex(ValueError,"cap"): m.record("a","run","tokens",100,0.7,cost_cap=1)
        m.record("b","run","tokens",20,0.2,cost_cap=1)
        self.assertEqual(m.summary("a")["total_cost"],0.4); self.assertEqual(m.summary("b")["total_cost"],0.2)


if __name__=="__main__": unittest.main()
