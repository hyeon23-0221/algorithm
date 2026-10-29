from typing import Any, Dict, List


def shell_sort_trace(arr: List[int]) -> Dict[str, Any]:
    """
    셸 정렬(Shell Sort) 스냅샷 생성
    - 간격(Gap)의 크기 변화
    - 설정된 간격만큼 떨어진 요소들 간의 그룹화 및 비교
    - 삽입(이동/교환)되어 가는 상태를 매 순간 기록
    """
    a = list(arr)
    n = len(a)
    history: List[Dict[str, Any]] = []
    step = 0

    history.append({
        "step": step,
        "array": list(a),
        "type": "init",
        "active_indices": [],
        "highlights": {
            "comparing": [],
            "pivot": None,
            "swapped": [],
            "sorted": [],
            "range": [0, n - 1],
            "gap": None,
            "overwriting": None
        },
        "description": f"셸 정렬 초기화 (요소 {n}개)"
    })

    gap = n // 2
    while gap > 0:
        step += 1
        history.append({
            "step": step,
            "array": list(a),
            "type": "gap_change",
            "active_indices": [],
            "highlights": {
                "comparing": [],
                "pivot": None,
                "swapped": [],
                "sorted": [],
                "range": [0, n - 1],
                "gap": gap,
                "overwriting": None
            },
            "description": f"간격(Gap)이 {gap}으로 설정되었습니다. {gap} 간격으로 부분 삽입 정렬을 진행합니다."
        })

        for i in range(gap, n):
            temp = a[i]
            j = i

            step += 1
            history.append({
                "step": step,
                "array": list(a),
                "type": "compare",
                "active_indices": [j - gap, j],
                "highlights": {
                    "comparing": [j - gap, j],
                    "pivot": None,
                    "swapped": [],
                    "sorted": [],
                    "range": [0, n - 1],
                    "gap": gap,
                    "overwriting": None
                },
                "description": f"간격 {gap}으로 떨어진 인덱스 {j - gap}(값: {a[j - gap]})과 인덱스 {j}(값: {temp})를 비교합니다."
            })

            while j >= gap and a[j - gap] > temp:
                a[j] = a[j - gap]
                step += 1
                history.append({
                    "step": step,
                    "array": list(a),
                    "type": "swap",
                    "active_indices": [j - gap, j],
                    "highlights": {
                        "comparing": [],
                        "pivot": None,
                        "swapped": [j - gap, j],
                        "sorted": [],
                        "range": [0, n - 1],
                        "gap": gap,
                        "overwriting": None
                    },
                    "description": f"값 {a[j]}가 더 크므로 {gap}칸 뒤(인덱스 {j})로 이동(Shift)시킵니다."
                })
                j -= gap

                if j >= gap:
                    step += 1
                    history.append({
                        "step": step,
                        "array": list(a),
                        "type": "compare",
                        "active_indices": [j - gap, i],
                        "highlights": {
                            "comparing": [j - gap, i],
                            "pivot": None,
                            "swapped": [],
                            "sorted": [],
                            "range": [0, n - 1],
                            "gap": gap,
                            "overwriting": None
                        },
                        "description": f"이전 간격 인덱스 {j - gap}(값: {a[j - gap]})과 삽입할 값 {temp}를 추가 비교합니다."
                    })

            a[j] = temp
            step += 1
            history.append({
                "step": step,
                "array": list(a),
                "type": "insert",
                "active_indices": [j],
                "highlights": {
                    "comparing": [],
                    "pivot": None,
                    "swapped": [j],
                    "sorted": [],
                    "range": [0, n - 1],
                    "gap": gap,
                    "overwriting": None
                },
                "description": f"임시 보관한 값 {temp}를 빈 자리인 인덱스 {j}에 삽입했습니다."
            })

        gap //= 2

    step += 1
    history.append({
        "step": step,
        "array": list(a),
        "type": "done",
        "active_indices": list(range(n)),
        "highlights": {
            "comparing": [],
            "pivot": None,
            "swapped": [],
            "sorted": list(range(n)),
            "range": [0, n - 1],
            "gap": 0,
            "overwriting": None
        },
        "description": "셸 정렬이 모두 완료되었습니다."
    })

    return {
        "name": "셸 정렬 (Shell Sort)",
        "complexity": {
            "best": "O(N log N)",
            "average": "O(N^1.25 ~ N^1.5)",
            "worst": "O(N^2)",
            "space": "O(1)"
        },
        "total_steps": len(history),
        "history": history
    }


def quick_sort_trace(arr: List[int]) -> Dict[str, Any]:
    """
    퀵 정렬(Quick Sort) 스냅샷 생성
    - 피벗(Pivot) 지정
    - 피벗과의 대소 비교 대상
    - 요소 교환 위치
    - 피벗의 최종 정렬 확정 상태 기록
    """
    a = list(arr)
    n = len(a)
    history: List[Dict[str, Any]] = []
    step = 0
    sorted_indices = set()

    history.append({
        "step": step,
        "array": list(a),
        "type": "init",
        "active_indices": [],
        "highlights": {
            "comparing": [],
            "pivot": None,
            "swapped": [],
            "sorted": [],
            "range": [0, n - 1],
            "gap": None,
            "overwriting": None
        },
        "description": f"퀵 정렬 초기화 (요소 {n}개)"
    })

    def _quick_sort(low: int, high: int):
        nonlocal step
        if low > high:
            return
        if low == high:
            sorted_indices.add(low)
            step += 1
            history.append({
                "step": step,
                "array": list(a),
                "type": "pivot_fixed",
                "active_indices": [low],
                "highlights": {
                    "comparing": [],
                    "pivot": None,
                    "swapped": [],
                    "sorted": sorted(list(sorted_indices)),
                    "range": [low, high],
                    "gap": None,
                    "overwriting": None
                },
                "description": f"단일 요소 구간 [{low}] (값: {a[low]}) 정렬 확정"
            })
            return

        pivot_val = a[high]
        step += 1
        history.append({
            "step": step,
            "array": list(a),
            "type": "pivot_select",
            "active_indices": [high],
            "highlights": {
                "comparing": [],
                "pivot": high,
                "swapped": [],
                "sorted": sorted(list(sorted_indices)),
                "range": [low, high],
                "gap": None,
                "overwriting": None
            },
            "description": f"구간 [{low}~{high}]에서 피벗으로 인덱스 {high}(값: {pivot_val})를 지정했습니다."
        })

        i = low - 1
        for j in range(low, high):
            step += 1
            history.append({
                "step": step,
                "array": list(a),
                "type": "compare",
                "active_indices": [j, high],
                "highlights": {
                    "comparing": [j, high],
                    "pivot": high,
                    "swapped": [],
                    "sorted": sorted(list(sorted_indices)),
                    "range": [low, high],
                    "gap": None,
                    "overwriting": None
                },
                "description": f"인덱스 {j}(값: {a[j]})와 피벗(값: {pivot_val})을 비교합니다."
            })

            if a[j] <= pivot_val:
                i += 1
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    step += 1
                    history.append({
                        "step": step,
                        "array": list(a),
                        "type": "swap",
                        "active_indices": [i, j],
                        "highlights": {
                            "comparing": [],
                            "pivot": high,
                            "swapped": [i, j],
                            "sorted": sorted(list(sorted_indices)),
                            "range": [low, high],
                            "gap": None,
                            "overwriting": None
                        },
                        "description": f"피벗 이하인 값을 좌측 영역으로 이동: 인덱스 {i}(값: {a[i]}) <-> 인덱스 {j}(값: {a[j]}) 교환"
                    })

        pivot_final = i + 1
        if pivot_final != high:
            a[pivot_final], a[high] = a[high], a[pivot_final]
            step += 1
            history.append({
                "step": step,
                "array": list(a),
                "type": "swap",
                "active_indices": [pivot_final, high],
                "highlights": {
                    "comparing": [],
                    "pivot": pivot_final,
                    "swapped": [pivot_final, high],
                    "sorted": sorted(list(sorted_indices)),
                    "range": [low, high],
                    "gap": None,
                    "overwriting": None
                },
                "description": f"피벗(값: {pivot_val})을 최종 정렬 위치인 인덱스 {pivot_final}로 이동했습니다."
            })

        sorted_indices.add(pivot_final)
        step += 1
        history.append({
            "step": step,
            "array": list(a),
            "type": "pivot_fixed",
            "active_indices": [pivot_final],
            "highlights": {
                "comparing": [],
                "pivot": pivot_final,
                "swapped": [],
                "sorted": sorted(list(sorted_indices)),
                "range": [low, high],
                "gap": None,
                "overwriting": None
            },
            "description": f"피벗(값: {pivot_val}, 인덱스 {pivot_final})의 최종 정렬 위치가 확정되었습니다."
        })

        _quick_sort(low, pivot_final - 1)
        _quick_sort(pivot_final + 1, high)

    _quick_sort(0, n - 1)

    step += 1
    history.append({
        "step": step,
        "array": list(a),
        "type": "done",
        "active_indices": list(range(n)),
        "highlights": {
            "comparing": [],
            "pivot": None,
            "swapped": [],
            "sorted": list(range(n)),
            "range": [0, n - 1],
            "gap": None,
            "overwriting": None
        },
        "description": "퀵 정렬이 모두 완료되었습니다."
    })

    return {
        "name": "퀵 정렬 (Quick Sort)",
        "complexity": {
            "best": "O(N log N)",
            "average": "O(N log N)",
            "worst": "O(N^2)",
            "space": "O(log N)"
        },
        "total_steps": len(history),
        "history": history
    }


def merge_sort_trace(arr: List[int]) -> Dict[str, Any]:
    """
    병합 정렬(Merge Sort) 스냅샷 생성
    - 배열이 논리적으로 분할되는 구간 (left, mid, right)
    - 두 부분 배열을 병합하며 좌우 요소를 비교하는 과정
    - 임시 배열에서 정렬 완료된 후 원본 배열로 덮어씌워지는(Overwrite) 상태 기록
    """
    a = list(arr)
    n = len(a)
    history: List[Dict[str, Any]] = []
    step = 0
    sorted_indices = set()

    history.append({
        "step": step,
        "array": list(a),
        "type": "init",
        "active_indices": [],
        "highlights": {
            "comparing": [],
            "pivot": None,
            "swapped": [],
            "sorted": [],
            "range": [0, n - 1],
            "gap": None,
            "overwriting": None
        },
        "description": f"병합 정렬 초기화 (요소 {n}개)"
    })

    def _merge_sort(low: int, high: int):
        nonlocal step
        if low >= high:
            return

        mid = (low + high) // 2
        step += 1
        history.append({
            "step": step,
            "array": list(a),
            "type": "split",
            "active_indices": list(range(low, high + 1)),
            "highlights": {
                "comparing": [],
                "pivot": None,
                "swapped": [],
                "sorted": sorted(list(sorted_indices)),
                "range": [low, high],
                "gap": None,
                "overwriting": None
            },
            "description": f"구간 [{low}~{high}]를 좌측 [{low}~{mid}]과 우측 [{mid + 1}~{high}]로 분할합니다."
        })

        _merge_sort(low, mid)
        _merge_sort(mid + 1, high)
        _merge(low, mid, high)

    def _merge(low: int, mid: int, high: int):
        nonlocal step
        temp: List[int] = []
        i = low
        j = mid + 1

        while i <= mid and j <= high:
            step += 1
            history.append({
                "step": step,
                "array": list(a),
                "type": "compare",
                "active_indices": [i, j],
                "highlights": {
                    "comparing": [i, j],
                    "pivot": None,
                    "swapped": [],
                    "sorted": sorted(list(sorted_indices)),
                    "range": [low, high],
                    "gap": None,
                    "overwriting": None
                },
                "description": f"좌측 요소(인덱스 {i}, 값: {a[i]})와 우측 요소(인덱스 {j}, 값: {a[j]})를 비교합니다."
            })

            if a[i] <= a[j]:
                temp.append(a[i])
                i += 1
            else:
                temp.append(a[j])
                j += 1

        while i <= mid:
            temp.append(a[i])
            i += 1
        while j <= high:
            temp.append(a[j])
            j += 1

        # 원본 배열로 덮어쓰기(Overwrite) 단계
        for idx, val in enumerate(temp):
            target_idx = low + idx
            a[target_idx] = val
            step += 1
            history.append({
                "step": step,
                "array": list(a),
                "type": "overwrite",
                "active_indices": [target_idx],
                "highlights": {
                    "comparing": [],
                    "pivot": None,
                    "swapped": [target_idx],
                    "sorted": sorted(list(sorted_indices)),
                    "range": [low, high],
                    "gap": None,
                    "overwriting": target_idx
                },
                "description": f"임시 배열에서 정렬된 값 {val}을 원본 배열 인덱스 {target_idx}로 덮어씁니다(Overwrite)."
            })

        if low == 0 and high == n - 1:
            for k in range(n):
                sorted_indices.add(k)
        else:
            step += 1
            history.append({
                "step": step,
                "array": list(a),
                "type": "merged_section",
                "active_indices": list(range(low, high + 1)),
                "highlights": {
                    "comparing": [],
                    "pivot": None,
                    "swapped": [],
                    "sorted": sorted(list(sorted_indices)),
                    "range": [low, high],
                    "gap": None,
                    "overwriting": None
                },
                "description": f"구간 [{low}~{high}]의 병합이 완료되었습니다."
            })

    _merge_sort(0, n - 1)

    step += 1
    history.append({
        "step": step,
        "array": list(a),
        "type": "done",
        "active_indices": list(range(n)),
        "highlights": {
            "comparing": [],
            "pivot": None,
            "swapped": [],
            "sorted": list(range(n)),
            "range": [0, n - 1],
            "gap": None,
            "overwriting": None
        },
        "description": "병합 정렬이 모두 완료되었습니다."
    })

    return {
        "name": "병합 정렬 (Merge Sort)",
        "complexity": {
            "best": "O(N log N)",
            "average": "O(N log N)",
            "worst": "O(N log N)",
            "space": "O(N)"
        },
        "total_steps": len(history),
        "history": history
    }
    
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from algorithms import shell_sort_trace, quick_sort_trace, merge_sort_trace

app = FastAPI(
    title="Algorithm Visualizer API",
    description="셸 정렬, 퀵 정렬, 병합 정렬의 상태 스냅샷 데이터를 제공하는 Cloud Run 백엔드",
    version="1.0.0"
)

# CORS 허용: GAS(Google Apps Script), 웹 브라우저, 로컬 환경 어디서든 호출 가능하도록 허용
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
        description="정렬할 정수 배열. 생략 시 기본 랜덤 배열(10개)이 자동 생성됩니다.",
        example=[38, 27, 43, 3, 9, 82, 10, 19, 50, 12]
    )


@app.get("/")
def health_check():
    """서버 상태 확인용 헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "Algorithm Visualizer Backend",
        "supported_algorithms": [
            "Shell Sort (셸 정렬)",
            "Quick Sort (퀵 정렬)",
            "Merge Sort (병합 정렬)"
        ]
    }


@app.post("/api/sort")
def generate_sort_history(request: SortRequest):
    """
    지정된 배열에 대해 3가지 알고리즘(셸, 퀵, 병합)의 상태 스냅샷 히스토리를 일괄 생성합니다.
    """
    try:
        # 배열이 전달되지 않은 경우 기본 테스트 배열 생성 (10~99 사이의 10개 정수)
        if not request.array or len(request.array) == 0:
            target_array = random.sample(range(5, 99), 10)
        else:
            target_array = request.array

        # 안전을 위한 크기 제한 (지나치게 큰 배열은 브라우저 렌더링 부하 방지)
        if len(target_array) > 50:
            raise HTTPException(
                status_code=400,
                detail="배열 크기는 시각화 성능을 위해 최대 50개 이하로 제한됩니다."
            )

        if not all(isinstance(x, int) for x in target_array):
            raise HTTPException(
                status_code=400,
                detail="배열의 모든 요소는 정수(integer)여야 합니다."
            )

        # 3가지 알고리즘 스냅샷 수집 실행
        shell_result = shell_sort_trace(target_array)
        quick_result = quick_sort_trace(target_array)
        merge_result = merge_sort_trace(target_array)

        return {
            "success": True,
            "original_array": target_array,
            "algorithms": {
                "shell_sort": shell_result,
                "quick_sort": quick_result,
                "merge_sort": merge_result
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"알고리즘 스냅샷 생성 중 서버 오류가 발생했습니다: {str(e)}"
        )


@app.get("/api/sort/demo")
def get_demo_sort_history():
    """간편한 확인 및 테스트를 위한 데모 엔드포인트"""
    demo_array = [38, 27, 43, 3, 9, 82, 10, 19, 50, 12]
    return generate_sort_history(SortRequest(array=demo_array))


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

