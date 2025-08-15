import os
from datetime import datetime
import sys

import pytest
from dotenv import load_dotenv

# Load variables from .env if present (useful for local development)
load_dotenv()

# Ensure project root is on sys.path so 'tests' package is importable during collection
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Re-export test helper for tests to import from tests.support.api
from tests.support.api import _test_results  # noqa: F401


@pytest.fixture(scope="session", autouse=True)
def save_test_results_to_file(request: pytest.FixtureRequest) -> None:
    """Session fixture that writes accumulated results to a timestamped text file in 'Test report/'."""

    def save_results() -> None:
        import json

        report_dir = "Test report"
        os.makedirs(report_dir, exist_ok=True)
        from datetime import datetime as _dt

        timestamp = _dt.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(report_dir, f"test_results_{timestamp}.txt")

        with open(report_path, "w", encoding="utf-8") as f:
            if not _test_results:
                f.write("No test results collected!\n")
            else:
                for result in _test_results:
                    f.write(f"Тест: {result['test_name']}\nСтатус: {result['status']}\n")
                    if result["status"] == "FAILED":
                        f.write("\nОЖИДАЕМЫЙ РЕЗУЛЬТАТ (ОР):\n")
                        f.write(json.dumps(result["expected_response"], ensure_ascii=False, indent=2))
                        f.write("\n\nФАКТИЧЕСКИЙ РЕЗУЛЬТАТ (ФР):\n")
                        f.write(json.dumps(result["actual_response"], ensure_ascii=False, indent=2))
                        f.write("\n\nРАЗЛИЧИЯ:\n")
                        f.write(str(result["differences"]))
                    f.write("\n" + "=" * 50 + "\n\n")

        print(f"Test report saved to: {os.path.abspath(report_path)}")

    request.addfinalizer(save_results)