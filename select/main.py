import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# 모든 도메인에서의 CORS 접근을 허용합니다.
CORS(app)

def insertion_sort_trace(arr):
    """
    단순 삽입 정렬(Insertion Sort)을 수행하며 각 단계(키 선택, 비교, 삽입/이동)의 
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

    # 두 번째 원소부터 시작하여 앞쪽의 정렬된 부분에 삽입합니다.
    for i in range(1, n):
        key = a[i]
        j = i - 1

        steps.append({
            "action": "select_key",
            "indices": [i],
            "array": list(a),
            "message": f"[{i}]번째 원소(값: {key})를 키(Key)로 선택하여 정렬된 위치를 탐색합니다."
        })

        # 키보다 큰 원소들을 오른쪽으로 한 칸씩 이동시킵니다.
        while j >= 0 and a[j] > key:
            steps.append({
                "action": "compare",
                "indices": [j, j + 1],
                "array": list(a),
                "message": f"인덱스 [{j}]의 값({a[j]})이 키({key})보다 크므로 오른쪽으로 시프트합니다."
            })
            a[j + 1] = a[j]
            j -= 1
            steps.append({
                "action": "shift",
                "indices": [j + 1, j + 2],
                "array": list(a),
                "message": f"원소 이동 후 배열 상태: {a}"
            })

        # 올바른 위치에 키를 삽입합니다.
        a[j + 1] = key
        steps.append({
            "action": "insert",
            "indices": [j + 1],
            "array": list(a),
            "message": f"인덱스 [{j + 1}] 위치에 키({key})를 최종 삽입했습니다. 현재 상태: {a}"
        })

    # 최종 완료 상태 기록
    steps.append({
        "action": "complete",
        "indices": [],
        "array": list(a),
        "message": f"삽입 정렬 최종 완료! 최종 결과: {a}"
    })

    return steps, a


@app.route('/insertion', methods=['POST'])
def handle_insertion():
    """
    클라이언트로부터 정렬할 배열 데이터를 수신하여 삽입 정렬 단계를 반환하는 API 엔드포인트
    """
    try:
        data = request.get_json() or {}
        raw_arr = data.get('array', [34, 25, 12, 22, 11, 90])
        
        # 입력된 데이터가 문자열 형태일 경우(쉼표 구분) 정수형 리스트로 변환
        if isinstance(raw_arr, str):
            arr = [int(x.strip()) for x in raw_arr.split(',') if x.strip()]
        else:
            arr = [int(x) for x in raw_arr]

        steps, sorted_arr = insertion_sort_trace(arr)

        # 시간 및 공간 복잡도 정보
        complexity = {
            "time_complexity": "최선 O(N) / 평균·최악 O(N^2)",
            "space_complexity": "O(1) (제자리 정렬)",
            "description": "자료 배열의 모든 요소를 앞에서부터 차례대로 이미 정렬된 배열 부분과 비교하여, 자신의 위치를 찾아 삽입하여 정렬하는 방식입니다. 이미 정렬된 데이터에 매우 효율적입니다."
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
    return "Insertion Sort Cloud Run Service is Healthy", 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
