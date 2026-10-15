import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# 모든 도메인에서의 CORS 접근을 허용합니다.
CORS(app)

def selection_sort_trace(arr):
    """
    단순 선택 정렬(Selection Sort)을 수행하며 각 단계(최솟값 탐색, 교환, 완료)의 
    트레이스 로그와 배열 상태를 기록합니다.
    """
    steps = []
    a = list(arr)
    n = len(a)

    # 초기 상태 기록
    steps.append({
        "action": "init",
        "indices": [],
        "array": list(a),
        "message": f"초기 배열 상태: {a}"
    })

    for i in range(n - 1):
        min_idx = i
        # 현재 미정렬 구간에서 최솟값의 인덱스를 탐색합니다.
        steps.append({
            "action": "scan_start",
            "indices": [i],
            "array": list(a),
            "message": f"[{i}]번째 자리를 기준으로 최솟값 탐색을 시작합니다. (기준값: {a[i]})"
        })

        for j in range(i + 1, n):
            steps.append({
                "action": "compare",
                "indices": [min_idx, j],
                "array": list(a),
                "message": f"현재 최솟값 후보 인덱스 [{min_idx}] (값: {a[min_idx]})와 비교 대상 인덱스 [{j}] (값: {a[j]})를 비교합니다."
            })

            if a[j] < a[min_idx]:
                min_idx = j
                steps.append({
                    "action": "update_min",
                    "indices": [min_idx],
                    "array": list(a),
                    "message": f"더 작은 값을 발견했습니다! 새로운 최솟값 후보 인덱스: [{min_idx}], 값: {a[min_idx]}"
                })

        # 최솟값이 기준 위치(i)와 다를 경우 자리를 교환(Swap)합니다.
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            steps.append({
                "action": "swap",
                "indices": [i, min_idx],
                "array": list(a),
                "message": f"인덱스 [{i}]와 최솟값 인덱스 [{min_idx}]의 위치를 교환합니다. 현재 상태: {a}"
            })
        else:
            steps.append({
                "action": "no_swap",
                "indices": [i],
                "array": list(a),
                "message": f"인덱스 [{i}]가 이미 최솟값이므로 자리를 교환하지 않습니다."
            })

    # 최종 완료 상태 기록
    steps.append({
        "action": "complete",
        "indices": [],
        "array": list(a),
        "message": f"선택 정렬 최종 완료! 최종 결과: {a}"
    })

    return steps, a


@app.route('/selection', methods=['POST'])
def handle_selection():
    """
    클라이언트로부터 정렬할 배열 데이터를 수신하여 선택 정렬 단계를 반환하는 API 엔드포인트
    """
    try:
        data = request.get_json() or {}
        raw_arr = data.get('array', [29, 10, 14, 37, 13])
        
        # 입력된 데이터가 문자열 형태일 경우(쉼표 구분) 정수형 리스트로 변환
        if isinstance(raw_arr, str):
            arr = [int(x.strip()) for x in raw_arr.split(',') if x.strip()]
        else:
            arr = [int(x) for x in raw_arr]

        steps, sorted_arr = selection_sort_trace(arr)

        # 시간 및 공간 복잡도 정보
        complexity = {
            "time_complexity": "항상 O(N^2) (최선, 평균, 최악 모두 동일)",
            "space_complexity": "O(1) (제자리 정렬)",
            "description": "전체 원소 중 가장 작은 원소를 찾아 맨 앞부터 순서대로 교환해 나가는 방식으로, 데이터 상태와 무관하게 항상 일정한 비교 연산을 수행합니다."
        }

        return jsonify({
            "success": True,
            "steps": steps,
            "result_value": sorted_arr,
            "complexity": complexity
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/', methods=['GET'])
def health_check():
    return "Selection Sort Cloud Run Service is Healthy", 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
