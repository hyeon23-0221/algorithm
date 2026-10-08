import os
from flask import Flask, jsonify, request

app = Flask(__name__)

def linear_search_steps(arr, target):
    """
    선형검색(Linear Search) 알고리즘을 수행하며,
    클라이언트가 단계별로 시각화할 수 있도록 각 탐색 과정을 기록하여 반환합니다.
    """
    steps = []
    found_index = -1
    
    for i in range(len(arr)):
        current_value = arr[i]
        # 현재 비교 중인 상태 기록 ('checking')
        steps.append({
            "index": i,
            "value": current_value,
            "status": "checking",
            "message": f"인덱스 {i}의 값({current_value})과 찾는 값({target})을 비교합니다."
        })
        
        if current_value == target:
            found_index = i
            # 값을 찾았을 때 상태 기록 ('found')
            steps.append({
                "index": i,
                "value": current_value,
                "status": "found",
                "message": f"성공! 인덱스 {i}에서 값 {target}을(를) 찾았습니다."
            })
            break
        else:
            # 일치하지 않을 때 상태 기록 ('mismatch')
            steps.append({
                "index": i,
                "value": current_value,
                "status": "mismatch",
                "message": f"불일치: 값 {current_value}은(는) 찾는 값이 아닙니다."
            })
            
    if found_index == -1:
        steps.append({
            "index": -1,
            "value": None,
            "status": "not_found",
            "message": f"탐색 실패: 배열 내에 값 {target}이(가) 존재하지 않습니다."
        })
        
    return steps

@app.route('/search', methods=['POST'])
def search():
    """
    클라이언트(GAS)로부터 배열과 타겟 값을 받아 선형검색을 실행하고 결과를 반환하는 엔드포인트
    """
    try:
        data = request.get_json()
        arr = data.get('array', [12, 25, 38, 41, 55, 60, 77, 82, 99])
        target = int(data.get('target', 55))
        
        # 선형검색 단계별 데이터 생성
        steps = linear_search_steps(arr, target)
        
        # 시간/공간 복잡도 정보 추가
        complexity = {
            "time_complexity": "O(N)",
            "space_complexity": "O(1)",
            "description": "데이터가 정렬되어 있지 않아도 처음부터 끝까지 순차적으로 탐색합니다."
        }
        
        return jsonify({
            "success": True,
            "array": arr,
            "target": target,
            "steps": steps,
            "complexity": complexity
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/', methods=['GET'])
def health_check():
    """서버 정상 작동 확인용 헬스체크 엔드포인트"""
    return "Linear Search Cloud Run Server is running!", 200

if __name__ == '__main__':
    # Cloud Run 환경 변수 포트(PORT) 반영, 기본값 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
