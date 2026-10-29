
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

