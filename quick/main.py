import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS 허용 (GAS 및 외부 요청 처리)

# ==========================================
# 1. 셸 정렬 (Shell Sort) 트레이스 생성기
# ==========================================
def generate_shell_sort_trace(arr):
    trace = []
    a = list(arr)
    n = len(a)
    
    trace.append({
        "array": list(a),
        "indices": [],
        "action": "start",
        "message": "셸 정렬(Shell Sort) 시작"
    })
    
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            
            while j >= gap and a[j - gap] > temp:
                trace.append({
                    "array": list(a),
                    "indices": [j, j - gap],
                    "action": "compare",
                    "message": f"간격(Gap: {gap}) 비교: a[{j-gap}]({a[j-gap]}) > a[{j}]({temp})"
                })
                a[j] = a[j - gap]
                j -= gap
                trace.append({
                    "array": list(a),
                    "indices": [j],
                    "action": "insert",
                    "message": f"값 덮어쓰기 발생"
                })
            a[j] = temp
        gap //= 2
        
    trace.append({
        "array": list(a),
        "indices": list(range(n)),
        "action": "complete",
        "message": "셸 정렬 완료!"
    })
    return trace

# ==========================================
# 2. 퀵 정렬 (Quick Sort) 트레이스 생성기
# ==========================================
def generate_quick_sort_trace(arr):
    trace = []
    a = list(arr)
    
    trace.append({
        "array": list(a),
        "indices": [],
        "action": "start",
        "message": "퀵 정렬(Quick Sort) 시작"
    })
    
    def quick_sort(low, high):
        if low < high:
            pi = partition(low, high)
            quick_sort(low, pi - 1)
            quick_sort(pi + 1, high)

    def partition(low, high):
        pivot = a[high]
        trace.append({
            "array": list(a),
            "indices": [high],
            "action": "select_pivot",
            "message": f"피벗(Pivot) 선택: {pivot} (인덱스 {high})"
        })
        
        i = low - 1
        for j in range(low, high):
            trace.append({
                "array": list(a),
                "indices": [j, high],
                "action": "compare",
                "message": f"피벗 {pivot}과 요소 a[{j}]({a[j]}) 비교"
            })
            if a[j] <= pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
                if i != j:
                    trace.append({
                        "array": list(a),
                        "indices": [i, j],
                        "action": "swap",
                        "message": f"요소 교환: a[{i}]({a[i]}) <-> a[{j}]({a[j]})"
                    })
                    
        a[i + 1], a[high] = a[high], a[i + 1]
        trace.append({
            "array": list(a),
            "indices": [i + 1, high],
            "action": "pivot_fixed",
            "message": f"피벗 위치 확정: {a[i + 1]}"
        })
        return i + 1

    if len(a) > 0:
        quick_sort(0, len(a) - 1)
        
    trace.append({
        "array": list(a),
        "indices": list(range(len(a))),
        "action": "complete",
        "message": "퀵 정렬 완료!"
    })
    return trace

# ==========================================
# 3. 병합 정렬 (Merge Sort) 트레이스 생성기
# ==========================================
def generate_merge_sort_trace(arr):
    trace = []
    a = list(arr)
    n = len(a)
    
    trace.append({
        "array": list(a),
        "indices": [],
        "action": "start",
        "message": "병합 정렬(Merge Sort) 시작"
    })
    
    def merge_sort(sub_arr, left_idx):
        if len(sub_arr) > 1:
            mid = len(sub_arr) // 2
            L = sub_arr[:mid]
            R = sub_arr[mid:]
            
            merge_sort(L, left_idx)
            merge_sort(R, left_idx + mid)
            
            i = j = k = 0
            while i < len(L) and j < len(R):
                trace.append({
                    "array": list(a),
                    "indices": [left_idx + i, left_idx + mid + j],
                    "action": "compare",
                    "message": f"병합 비교: {L[i]} vs {R[j]}"
                })
                if L[i] < R[j]:
                    sub_arr[k] = L[i]
                    i += 1
                else:
                    sub_arr[k] = R[j]
                    j += 1
                a[left_idx + k] = sub_arr[k]
                trace.append({
                    "array": list(a),
                    "indices": [left_idx + k],
                    "action": "overwrite",
                    "message": f"원본 배열 덮어쓰기: {sub_arr[k]}"
                })
                k += 1
                
            while i < len(L):
                sub_arr[k] = L[i]
                a[left_idx + k] = sub_arr[k]
                i += 1
                k += 1
            while j < len(R):
                sub_arr[k] = R[j]
                a[left_idx + k] = sub_arr[k]
                j += 1
                k += 1

    if n > 0:
        merge_sort(a, 0)
        
    trace.append({
        "array": list(a),
        "indices": list(range(n)),
        "action": "complete",
        "message": "병합 정렬 완료!"
    })
    return trace

# ==========================================
# API 엔드포인트 라우팅
# ==========================================
@app.route('/sort-compare', methods=['POST'])
def sort_compare():
    try:
        data = request.get_json(silent=True) or {}
        array_data = data.get('array')
        
        # 유효하지 않은 배열인 경우 기본 더미 배열 사용
        if not array_data or not isinstance(array_data, list):
            array_data = [38, 27, 43, 3, 9, 82, 10, 19, 50, 15]
            
        # 3대 알고리즘 트레이스 동시 생성
        shell_trace = generate_shell_sort_trace(array_data)
        quick_trace = generate_quick_sort_trace(array_data)
        merge_trace = generate_merge_sort_trace(array_data)
        
        return jsonify({
            "success": True,
            "traces": {
                "shell": shell_trace,
                "quick": quick_trace,
                "merge": merge_trace
            }
        })
    except Exception as e:
        # 500 에러 발생 시 상세 원인 반환
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    return "Cloud Run Sort Comparison Backend is Running successfully!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
