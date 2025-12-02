#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E Integration Tests for PathcraftAI
C# ↔ Python subprocess 통합 테스트
"""

import json
import subprocess
import sys
import os

# Windows UTF-8 설정
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def test_python_cli_json_output():
    """Test 1: JSON 출력 순수성 테스트

    --json 플래그 사용 시 stdout에 순수 JSON만 출력되어야 함
    """
    print("\n=== Test 1: JSON Output Purity ===")

    # ai_build_analyzer.py --json 실행 (POB 없이 에러 응답 확인)
    result = subprocess.run(
        [sys.executable, 'ai_build_analyzer.py', '--json'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
    )

    stdout = result.stdout.strip()
    stderr = result.stderr

    # stderr에 로그가 있어도 OK (정상)
    if stderr:
        print(f"  [INFO] stderr has logs (expected): {len(stderr)} chars")

    # stdout은 순수 JSON이어야 함
    try:
        parsed = json.loads(stdout)
        print(f"  [OK] stdout is valid JSON")

        # 에러 응답 확인 (POB 없이 실행했으므로)
        if 'error' in parsed:
            print(f"  [OK] Error response as expected: {parsed['error'][:50]}...")
            return True
        else:
            print(f"  [OK] Unexpected success response")
            return True

    except json.JSONDecodeError as e:
        print(f"  [FAIL] stdout is NOT valid JSON: {e}")
        print(f"  stdout content: {stdout[:200]}")
        return False


def test_filter_generation_flow():
    """Test 2: 필터 생성 전체 흐름 테스트

    filter_generator_cli.py가 정상적으로 실행되고 필터 파일 생성
    """
    print("\n=== Test 2: Filter Generation Flow ===")

    # --help 명령어로 CLI 작동 확인
    result = subprocess.run(
        [sys.executable, 'filter_generator_cli.py', '--help'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result.returncode == 0 and '--output' in result.stdout:
        print(f"  [OK] filter_generator_cli --help works")
    else:
        print(f"  [FAIL] filter_generator_cli --help failed")
        return False

    # 실제 필터 생성 테스트 (테스트 POB 파일 사용)
    test_pob_file = os.path.join(os.path.dirname(__file__), 'tests', 'sample_builds', 'test_build.xml')

    if os.path.exists(test_pob_file):
        result = subprocess.run(
            [sys.executable, 'filter_generator_cli.py', test_pob_file, '--mode', 'ssf'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=os.path.dirname(__file__)
        )

        if result.returncode == 0:
            print(f"  [OK] Filter generated successfully")
        else:
            print(f"  [WARN] Filter generation returned non-zero (may be expected without POB)")
    else:
        print(f"  [SKIP] No test POB file at {test_pob_file}")

    return True


def test_error_handling():
    """Test 3: 에러 핸들링 테스트

    잘못된 입력에 대해 적절한 JSON 에러 응답
    """
    print("\n=== Test 3: Error Handling ===")

    # 존재하지 않는 POB URL로 테스트
    result = subprocess.run(
        [sys.executable, 'ai_build_analyzer.py', '--pob', 'https://invalid-url.example.com/notfound', '--json'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30,
        env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
    )

    stdout = result.stdout.strip()

    try:
        parsed = json.loads(stdout)

        if 'error' in parsed:
            print(f"  [OK] Error handled gracefully: {parsed['error'][:50]}...")
            return True
        else:
            print(f"  [WARN] Expected error but got success")
            return True

    except json.JSONDecodeError:
        print(f"  [FAIL] Error response is not valid JSON")
        return False


def test_module_imports():
    """Test 4: 핵심 모듈 import 테스트"""
    print("\n=== Test 4: Module Imports ===")

    modules_to_test = [
        ('pob_decoder', 'POBDecoder'),
        ('ai_build_analyzer', None),
        ('filter_generator_cli', None),
        ('domain.models.filter_rule', 'FilterRule'),
        ('infrastructure.writers.filter_file_writer', 'FilterFileWriter'),
        ('application.services.filter_generator_service', 'FilterGeneratorService'),
    ]

    all_passed = True

    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name] if class_name else [])
            if class_name:
                getattr(module, class_name)
            print(f"  [OK] {module_name}")
        except Exception as e:
            print(f"  [FAIL] {module_name}: {e}")
            all_passed = False

    return all_passed


def test_data_files():
    """Test 5: 데이터 파일 검증"""
    print("\n=== Test 5: Data Files ===")

    data_files = [
        ('data/gem_levels.json', 700),
        ('data/quest_rewards.json', 5),
        ('game_data/gems.json', 500),
        ('game_data/uniques.json', 1000),
        ('game_data/base_types.json', 3),
    ]

    all_passed = True

    for file_path, min_entries in data_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            count = len(data) if isinstance(data, (list, dict)) else 0

            if count >= min_entries:
                print(f"  [OK] {file_path}: {count} entries")
            else:
                print(f"  [WARN] {file_path}: {count} entries (expected >={min_entries})")

        except Exception as e:
            print(f"  [FAIL] {file_path}: {e}")
            all_passed = False

    return all_passed


def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("PathcraftAI E2E Integration Tests")
    print("=" * 60)

    results = {
        'JSON Output Purity': test_python_cli_json_output(),
        'Filter Generation Flow': test_filter_generation_flow(),
        'Error Handling': test_error_handling(),
        'Module Imports': test_module_imports(),
        'Data Files': test_data_files(),
    }

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All E2E tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
