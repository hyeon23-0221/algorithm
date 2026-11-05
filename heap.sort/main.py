"""
Google Cloud Run 배포용 정렬 알고리즘 시각화 백엔드 서버 (FastAPI)

힙 정렬(Heap Sort)과 도수 정렬(Counting Sort)의 단계별 상태 스냅샷 및
시간 복잡도 진행도 메타데이터를 생성하여 클라이언트에 스트리밍/재생 가능한 JSON 형태로 반환합니다.
"""
import math
import os
import random
import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Heap & Counting Sort Visualizer API",
    description="힙 정렬 및 도수 정렬의 단계별 히스토그램 스냅샷과 시간 복잡도 메타데이터를 제공하는 백엔드",
    version="1.0.0"
)

# CORS 허용: Google Apps Script(GAS), 로컬 호스트, 웹 브라우저 통신 지원
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SortRequest(BaseModel):
    array: Optional[List[int]] = Field(
        default=None,
        description="정렬할 정수 배열. 생략 시 기본 랜덤 배열(12개)이 자동 생성됩니다.",
        example=[45, 12, 85, 32, 89, 39, 69, 44, 42, 1, 90, 75]
    )


def heap_sort_trace(arr: List[int]) -> Dict[str, Any]:
    """
    힙 정렬(Heap Sort) 단계별 상태 스냅샷 및 메타데이터 추출
    - Max-Heap 구축 단계
    - 최댓값 추출 및 제자리(In-place) 스왑 단계
    - 각 스텝별 비교/교환 횟수, 경과 시간(ms), O(N log N) 진행도 계산
    """
    start_time = time.perf_counter()
    a = list(arr)
    n = len(a)
    history: List[Dict[str, Any]] = []
    step = 0
    comparisons = 0
    swaps = 0
    sorted_indices = set()

    # 예상 연산량 (N log2 N 기반 진행률 추정)
    expected_ops = max(1, int(2 * n * math.log2(max(2, n))))

    def calc_progress(ops: int) -> float:
        return min(99.0, round((ops / expected_ops) * 100, 1))

    # 초기 상태 스냅샷
    history.append({
        "step": step,
        "array": list(a),
        "type": "init",
        "active_indices": [],
        "highlights": {
            "comparing": [],
            "swapped": [],
            "sorted": [],
            "heap_root": 0
        },
        "metrics": {
            "comparisons": 0,
            "swaps": 0,
            "elapsed_ms": 0.0,
            "complexity_progress": 0.0,
            "complexity_formula": "O(N log N)"
        },
        "description": f"힙 정렬 초기화 (요소 {n}개) - 최대 힙(Max-Heap) 트리 구성을 준비합니다."
    })

    def max_heapify(limit: int, root_idx: int):
        nonlocal step, comparisons, swaps
        largest = root_idx
        left = 2 * root_idx + 1
        right = 2 * root_idx + 2

        if left < limit:
            comparisons += 1
            step += 1
            history.append({
                "step": step,
                "array": list(a),
                "type": "compare",
                "active_indices": [root_idx, left],
                "highlights": {
                    "comparing": [root_idx, left],
                    "swapped": [],
                    "sorted": sorted(list(sorted_indices)),
                    "heap_root": root_idx
                },
                "metrics": {
                    "comparisons": comparisons,
                    "swaps": swaps,
                    "elapsed_ms": round((time.perf_counter() - start_time) * 1000, 3),
                    "complexity_progress": calc_progress(comparisons + swaps),
                    "complexity_formula": "O(N log N)"
                },
                "description": f"부모 노드 [{root_idx}](값 {a[root_idx]})와 좌측 자식 [{left}](값 {a[left]}) 비교"
            })
            if a[left] > a[largest]:
                largest = left

        if right < limit:
            comparisons += 1
            step += 1
            history.append({
                "step": step,
                "array": list(a),
                "type": "compare",
                "active_indices": [largest, right],
                "highlights": {
                    "comparing": [largest, right],
                    "swapped": [],
                    "sorted": sorted(list(sorted_indices)),
                    "heap_root": root_idx
                },
                "metrics": {
                    "comparisons": comparisons,
                    "swaps": swaps,
                    "elapsed_ms": round((time.perf_counter() - start_time) * 1000, 3),
                    "complexity_progress": calc_progress(comparisons + swaps),
                    "complexity_formula": "O(N log N)"
                },
                "description": f"현재 최댓값 [{largest}](값 {a[largest]})과 우측 자식 [{right}](값 {a[right]}) 비교"
            })
            if a[right] > a[largest]:
                largest = right

        if largest != root_idx:
            a[root_idx], a[largest] = a[largest], a[root_idx]
            swaps += 1
            step += 1
            history.append({
                "step": step,
                "array": list(a),
                "type": "swap",
                "active_indices": [root_idx, largest],
                "highlights": {
                    "comparing": [],
                    "swapped": [root_idx, largest],
                    "sorted": sorted(list(sorted_indices)),
                    "heap_root": root_idx
                },
                "metrics": {
                    "comparisons": comparisons,
                    "swaps": swaps,
                    "elapsed_ms": round((time.perf_counter() - start_time) * 1000, 3),
                    "complexity_progress": calc_progress(comparisons + swaps),
                    "complexity_formula": "O(N log N)"
                },
                "description": f"힙 속성 위반: 부모 노드 [{root_idx}]와 자식 노드 [{largest}] 교환(Swap)"
            })
            max_heapify(limit, largest)

    # 1. Build Max-Heap (바닥 서브트리부터 역순)
    for i in range(n // 2 - 1, -1, -1):
        step += 1
        history.append({
            "step": step,
            "array": list(a),
            "type": "build_heap",
            "active_indices": [i],
            "highlights": {
                "comparing": [],
                "swapped": [],
                "sorted": sorted(list(sorted_indices)),
                "heap_root": i
            },
            "metrics": {
                "comparisons": comparisons,
                "swaps": swaps,
                "elapsed_ms": round((time.perf_counter() - start_time) * 1000, 3),
                "complexity_progress": calc_progress(comparisons + swaps),
                "complexity_formula": "O(N log N)"
            },
            "description": f"서브트리 루트 [{i}](값 {a[i]})에 대해 최대 힙화(Max-Heapify) 수행"
        })
        max_heapify(n, i)

    # 2. Extract Max & Re-heapify
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        swaps += 1
        sorted_indices.add(i)
        step += 1
        history.append({
            "step": step,
            "array": list(a),
            "type": "extract_max",
            "active_indices": [0, i],
            "highlights": {
                "comparing": [],
                "swapped": [0, i],
                "sorted": sorted(list(sorted_indices)),
                "heap_root": 0
            },
            "metrics": {
                "comparisons": comparisons,
                "swaps": swaps,
                "elapsed_ms": round((time.perf_counter() - start_time) * 1000, 3),
                "complexity_progress": calc_progress(comparisons + swaps),
                "complexity_formula": "O(N log N)"
            },
            "description": f"최댓값(루트 a[0]={a[i]})을 최종 정렬 위치 [{i}]로 이동 후 힙 크기 축소"
        })
        max_heapify(i, 0)

    sorted_indices.add(0)
    step += 1
    total_time_ms = round((time.perf_counter() - start_time) * 1000, 3)
    history.append({
        "step": step,
        "array": list(a),
        "type": "done",
        "active_indices": list(range(n)),
        "highlights": {
            "comparing": [],
            "swapped": [],
            "sorted": list(range(n)),
            "heap_root": None
        },
        "metrics": {
            "comparisons": comparisons,
            "swaps": swaps,
            "elapsed_ms": total_time_ms,
            "complexity_progress": 100.0,
            "complexity_formula": "O(N log N)"
        },
        "description": f"힙 정렬 완료! (총 {comparisons}회 비교, {swaps}회 교환, {total_time_ms}ms 소요)"
    })

    return {
        "name": "힙 정렬 (Heap Sort)",
        "complexity": {
            "best": "O(N log N)",
            "average": "O(N log N)",
            "worst": "O(N log N)",
            "space": "O(1)"
        },
        "total_steps": len(history),
        "total_time_ms": total_time_ms,
        "history": history
    }


def counting_sort_trace(arr: List[int]) -> Dict[str, Any]:
    """
    도수 정렬(Counting Sort) 단계별 상태 스냅샷 및 메타데이터 추출
    - 도수 분포(Count) 계산 단계
    - 누적 도수표 계산 단계
    - 정렬된 출력 배열로 요소 배치 단계
    - 각 스텝별 연산 횟수(Passes, Writes), 소요 시간(ms), O(N + K) 진행도 계산
    """
    start_time = time.perf_counter()
    a = list(arr)
    n = len(a)
    history: List[Dict[str, Any]] = []
    step = 0
    passes = 0
    writes = 0
    sorted_indices = set()

    if n == 0:
        return {"name": "도수 정렬", "total_steps": 0, "history": []}

    min_val = min(a)
    max_val = max(a)
    range_k = max_val - min_val + 1
    total_expected_ops = max(1, 2 * n + range_k)

    def calc_progress(ops: int) -> float:
        return min(99.0, round((ops / total_expected_ops) * 100, 1))

    # 초기 상태 스냅샷
    history.append({
        "step": step,
        "array": list(a),
        "type": "init",
        "active_indices": [],
        "highlights": {
            "reading": None,
            "writing": None,
            "sorted": []
        },
        "metrics": {
            "frequency_passes": 0,
            "array_writes": 0,
            "elapsed_ms": 0.0,
            "complexity_progress": 0.0,
            "complexity_formula": f"O(N + K) [N={n}, K={range_k}]"
        },
        "description": f"도수 정렬 초기화: 최솟값 {min_val}, 최댓값 {max_val} (범위 K={range_k})"
    })

    # 1. 도수(빈도수) 계산
    count = [0] * range_k
    for idx, val in enumerate(a):
        passes += 1
        count[val - min_val] += 1
        step += 1
        history.append({
            "step": step,
            "array": list(a),
            "type": "count",
            "active_indices": [idx],
            "highlights": {
                "reading": idx,
                "writing": None,
                "sorted": []
            },
            "metrics": {
                "frequency_passes": passes,
                "array_writes": writes,
                "elapsed_ms": round((time.perf_counter() - start_time) * 1000, 3),
                "complexity_progress": calc_progress(passes + writes),
                "complexity_formula": f"O(N + K) [N={n}, K={range_k}]"
            },
            "description": f"도수 카운트: 인덱스 [{idx}](값 {val}) 빈도수 1 증가 (총 {count[val - min_val]}회)"
        })

    # 2. 누적 도수표 계산
    for i in range(1, range_k):
        count[i] += count[i - 1]
        passes += 1
        step += 1
        history.append({
            "step": step,
            "array": list(a),
            "type": "accumulate",
            "active_indices": [],
            "highlights": {
                "reading": None,
                "writing": None,
                "sorted": []
            },
            "metrics": {
                "frequency_passes": passes,
                "array_writes": writes,
                "elapsed_ms": round((time.perf_counter() - start_time) * 1000, 3),
                "complexity_progress": calc_progress(passes + writes),
                "complexity_formula": f"O(N + K) [N={n}, K={range_k}]"
            },
            "description": f"누적 도수 합산: 값 {i + min_val}까지의 누적 등장 횟수 = {count[i]}개"
        })

    # 3. 출력 배열에 안정 배치(Stable Placement)
    output = [0] * n
    # 시각화를 위해 초기 output은 원본 모양을 유지하되 덮어써짐
    current_display = list(a)

    for idx in range(n - 1, -1, -1):
        val = a[idx]
        target_pos = count[val - min_val] - 1
        output[target_pos] = val
        current_display[target_pos] = val
        count[val - min_val] -= 1
        writes += 1
        sorted_indices.add(target_pos)
        step += 1
        history.append({
            "step": step,
            "array": list(current_display),
            "type": "place",
            "active_indices": [target_pos],
            "highlights": {
                "reading": idx,
                "writing": target_pos,
                "sorted": sorted(list(sorted_indices))
            },
            "metrics": {
                "frequency_passes": passes,
                "array_writes": writes,
                "elapsed_ms": round((time.perf_counter() - start_time) * 1000, 3),
                "complexity_progress": calc_progress(passes + writes),
                "complexity_formula": f"O(N + K) [N={n}, K={range_k}]"
            },
            "description": f"배열 배치: 원본 [{idx}](값 {val})을 정렬 위치 [{target_pos}]에 기입 (누적 카운트 감소)"
        })

    step += 1
    total_time_ms = round((time.perf_counter() - start_time) * 1000, 3)
    history.append({
        "step": step,
        "array": list(output),
        "type": "done",
        "active_indices": list(range(n)),
        "highlights": {
            "reading": None,
            "writing": None,
            "sorted": list(range(n))
        },
        "metrics": {
            "frequency_passes": passes,
            "array_writes": writes,
            "elapsed_ms": total_time_ms,
            "complexity_progress": 100.0,
            "complexity_formula": f"O(N + K) [N={n}, K={range_k}]"
        },
        "description": f"도수 정렬 완료! (총 {passes}회 순회, {writes}회 쓰기, {total_time_ms}ms 소요)"
    })

    return {
        "name": "도수 정렬 (Counting Sort)",
        "complexity": {
            "best": "O(N + K)",
            "average": "O(N + K)",
            "worst": "O(N + K)",
            "space": "O(K)"
        },
        "total_steps": len(history),
        "total_time_ms": total_time_ms,
        "history": history
    }


@app.get("/")
def health_check():
    """서버 상태 확인용 헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "Heap & Counting Sort Visualizer Backend",
        "supported_algorithms": [
            "Heap Sort (힙 정렬) - O(N log N)",
            "Counting Sort (도수 정렬) - O(N + K)"
        ]
    }


@app.post("/api/sort")
def generate_sort_history(request: SortRequest):
    """
    지정된 배열에 대해 힙 정렬과 도수 정렬의 단계별 스냅샷 히스토리를 동시 생성합니다.
    """
    try:
        # 배열이 없으면 10~99 범위의 12개 정수로 기본 생성
        if not request.array or len(request.array) == 0:
            target_array = [random.randint(15, 95) for _ in range(12)]
        else:
            target_array = request.array

        if len(target_array) > 50:
            raise HTTPException(
                status_code=400,
                detail="시각화 최적화를 위해 배열 크기는 최대 50개 이하로 제한됩니다."
            )

        if not all(isinstance(x, int) for x in target_array):
            raise HTTPException(
                status_code=400,
                detail="배열의 모든 요소는 정수(integer)여야 합니다."
            )

        heap_res = heap_sort_trace(target_array)
        counting_res = counting_sort_trace(target_array)

        return {
            "success": True,
            "original_array": target_array,
            "algorithms": {
                "heap_sort": heap_res,
                "counting_sort": counting_res
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"정렬 스냅샷 생성 중 서버 오류: {str(e)}"
        )


@app.get("/api/sort/demo")
def get_demo_sort_history():
    """테스트 및 시연용 데모 엔드포인트"""
    demo_array = [45, 12, 85, 32, 89, 39, 69, 44, 42, 1, 90, 75]
    return generate_sort_history(SortRequest(array=demo_array))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
