import sys
import inspect
from tests import test_signal,test_forecast,test_alerts,test_router,test_impact,test_detector

modules=[test_signal,test_forecast,test_alerts,test_router,test_impact,test_detector]
passed=0
failed=0
for mod in modules:
    for name,func in inspect.getmembers(mod,inspect.isfunction):
        if name.startswith("test_"):
            try:
                func()
                print(f"PASS: {name}")
                passed+=1
            except Exception as e:
                print(f"FAIL: {name} - {e}")
                failed+=1
print(f"\nResults: {passed} passed, {failed} failed")
if failed>0:
    sys.exit(1)