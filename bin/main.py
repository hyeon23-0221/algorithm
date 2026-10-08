import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# 클라이언트 및 외부 환경에서의 요청을 허용하기 위한 CORS 설정
CORS(app)

def binary_search_steps(arr, target):
    """
    이진 검색(Binary Search) 알고리즘을 수행하며,
    클라이언트가 도형을 통해 탐색 범위를 단계별로 시각화할 수 있도록
    left, right, mid 지점 및 상태 정보를 기록하여 반환합니다.
    """
    steps = []
    left = 0
    right = len(arr) - 1
    found_index = -1
    
    # 이진 검색은 반드시 정렬된 배열에서 동작해야 함
    sorted_arr = sorted(arr)
    
    while left <= right:
        mid = (left + right) // 2
        mid_val = sorted_arr[mid]
        
        # 1. 중앙값 비교 단계 기록 ('checking')
        steps.append({
            "left": left,
            "right": right,
            "mid": mid,
            "value": mid_val,
            "status": "checking",
            "message": f"범위 [{left}~{right}] | 중앙 인덱스 {mid}의 값({mid_val})과 타겟({target})을 비교합니다."
        })
        
        if mid_val == target:
            found_index = mid
            # 2. 타겟을 찾은 단계 기록 ('found')
            steps.append({
                "left": left,
                "right": right,
                "mid": mid,
                "value": mid_val,
                "status": "found",
                "message": f"성공! 인덱스 {mid}에서 값 {target}을(를) 찾았습니다."
            })
            break
        elif mid_val < target:
            # 타겟이 중앙값보다 큰 경우: 오른쪽 절반 탐색
            steps.append({
                "left": left,
                "right": right,
                "mid": mid,
                "value": mid_val,
                "status": "mismatch_right",
                "message": f"불일치: {mid_val} < {target} 이므로 오른쪽 구간({mid + 1}~{right})을 탐색합니다."
            })
            left = mid + 1
        else:
            # 타겟이 중앙값보다 작은 경우: 왼쪽 절반 탐색
            steps.append({
                "left": left,
                "right": right,
                "mid": mid,
                "value": mid_val,
                "status": "mismatch_left",
                "message": f"불일치: {mid_val} > {target} 이므로 왼쪽 구간({left}~{mid - 1})을 탐색합니다."
            })
            right = mid - 1
            
    if found_index == -1:
        steps.append({
            "left": left,
            "right": right,
            "mid": -1,
            "value": None,
            "status": "not_found",
            "message": f"탐색 실패: 배열 내에 값 {target}이(가) 존재하지 않습니다."
        })
        
    return sorted_arr, steps

@app.route('/search', methods=['POST'])
def search():
    """
    클라이언트로부터 배열과 타겟 값을 받아 이진 검색을 실행하고,
    단계별 탐색 상태 및 복잡도 정보를 포함하여 JSON으로 반환합니다.
    """
    try:
        data = request.get_json()
        arr = data.get('array', [12, 25, 38, 41, 55, 60, 77, 82, 99])
        target = int(data.get('target', 55))
        
        # 이진 검색 수행
        sorted_arr, steps = binary_search_steps(arr, target)
        
        # 시간 및 공간 복잡도 정보 정의
        complexity = {
            "time_complexity": "O(log N)",
            "space_complexity": "O(1)",
            "description": "정렬된 배열에서 각 단계마다 탐색 범위를 절반씩 줄여가므로 매우 빠르게 데이터를 찾습니다."
        }
        
        return jsonify({
            "success": True,
            "array": sorted_arr,
            "target": target,
            "steps": steps,
            "complexity": complexity
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/', methods=['GET'])
def health_check():
    """서버 정상 동작 확인용 엔드포인트"""
    return "Binary Search Cloud Run Server is running!", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
