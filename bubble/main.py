import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# 모든 도메인에서의 CORS 접근 허용
CORS(app)

def bubble_sort_trace(arr):
    """
    버블 정렬을 수행하며 각 단계(비교, 교환, 완료)의 트레이스 로그와 배열 상태를 기록합니다.
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

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            # 1. 두 원소 비교 단계 기록
            steps.append({
                "action": "compare",
                "indices": [j, j + 1],
                "array": list(a),
                "message": f"인덱스 [{j}] (값: {a[j]})와 인덱스 [{j + 1}] (값: {a[j + 1]})을 비교합니다."
            })

            if a[j] > a[j + 1]:
                # 2. 앞의 값이 더 크면 교환(Swap)
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
                steps.append({
                    "action": "swap",
                    "indices": [j, j + 1],
                    "array": list(a),
                    "message": f"앞의 값이 더 크므로 위치를 교환합니다. 현재 상태: {a}"
                })

        # 최적화: 이번 패스에서 교환이 전혀 없었다면 이미 정렬된 상태이므로 조기 종료
        if not swapped:
            steps.append({
                "action": "sorted",
                "indices": [],
                "array": list(a),
                "message": "이번 순회에서 교환이 발생하지 않아 정렬이 조기 완료되었습니다."
            })
            break

    # 최종 완료 상태 기록
    steps.append({
        "action": "complete",
        "indices": [],
        "array": list(a),
        "message": f"버블 정렬 최종 완료! 최종 결과: {a}"
    })

    return steps, a


@app.route('/bubble', methods=['POST'])
def handle_bubble():
    """
    클라이언트로부터 정렬할 배열 데이터를 수신하여 버블 정렬 단계를 반환하는 API 엔드포인트
    """
    try:
        data = request.get_json() or {}
        raw_arr = data.get('array', [64, 34, 25, 12, 22, 11, 90])
        
        # 입력된 데이터가 문자열 형태일 경우(쉼표 구분) 정수형 리스트로 변환
        if isinstance(raw_arr, str):
            arr = [int(x.strip()) for x in raw_arr.split(',') if x.strip()]
        else:
            arr = [int(x) for x in raw_arr]

        steps, sorted_arr = bubble_sort_trace(arr)

        # 시간 및 공간 복잡도 정보
        complexity = {
            "time_complexity": "최선 O(N) / 평균·최악 O(N^2)",
            "space_complexity": "O(1) (제자리 정렬)",
            "description": "인접한 두 원소를 검사하여 정렬하는 알고리즘으로, 구현이 단순하지만 데이터가 많을 경우 비효율적입니다."
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
    return "Bubble Sort Cloud Run Service is Healthy", 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
