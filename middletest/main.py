import os
from flask import Flask, request, jsonify

app = Flask(__name__)

def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response

class FixedQueue:
    """시험지 요구사항을 만족하는 고정 길이 큐 알고리즘 클래스 (사이즈 20)"""
    def __init__(self, capacity=20):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = 0
        self.rear = 0
        self.size = 0

    def is_full(self):
        return self.size == self.capacity

    def is_empty(self):
        return self.size == 0

    def push(self, item):
        if self.is_full():
            return False, f"Overflow: 큐가 가득 찼습니다. ({item} 추가 불가)"
        self.queue[self.rear] = item
        self.rear = (self.rear + 1) % self.capacity
        self.size += 1
        return True, f"Push 성공: {item}"

    def pop(self):
        if self.is_empty():
            return False, "Underflow: 큐가 비어 있습니다.", None
        item = self.queue[self.front]
        self.queue[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return True, f"Pop 성공: {item}", item

    def get_length(self):
        return self.size

    def peek_front(self):
        if self.is_empty():
            return None, "큐가 비어 있어 전면 데이터를 확인할 수 없습니다."
        return self.queue[self.front], f"Front 데이터 확인: {self.queue[self.front]}"

    def clear(self):
        self.queue = [None] * self.capacity
        self.front = 0
        self.rear = 0
        self.size = 0
        return True, "큐 전체 데이터가 삭제(초기화)되었습니다."

    def search_index(self, val):
        """큐 내부에서 값이 존재하는 상대적 인덱스(Front 기준 0부터 size-1) 검색"""
        indices = []
        for i in range(self.size):
            actual_idx = (self.front + i) % self.capacity
            if self.queue[actual_idx] == val:
                indices.append(i)
        return indices

    def count_value(self, val):
        """값의 개수 반환"""
        count = 0
        for i in range(self.size):
            actual_idx = (self.front + i) % self.capacity
            if self.queue[actual_idx] == val:
                count += 1
        return count

    def contains(self, val):
        """값의 존재 여부 검사 (True/False)"""
        return len(self.search_index(val)) > 0

    def dump_front_to_rear(self):
        """Front부터 Rear까지 순서대로 배열 형태로 출력"""
        result = []
        for i in range(self.size):
            actual_idx = (self.front + i) % self.capacity
            result.append(self.queue[actual_idx])
        return result

    def get_snapshot(self, action_desc, status_msg):
        return {
            "queue": list(self.queue),
            "front": self.front,
            "rear": self.rear,
            "size": self.size,
            "capacity": self.capacity,
            "action": action_desc,
            "status": status_msg,
            "dump": self.dump_front_to_rear()
        }

@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def handle_queue():
    if request.method == 'OPTIONS':
        return add_cors_headers(jsonify({'status': 'CORS OK'})), 200

    if request.method == 'GET':
        return add_cors_headers(jsonify({"status": "Cloud Run Fixed Queue Server Online"})), 200

    try:
        data = request.get_json(force=True) if request.is_json else {}
        capacity = int(data.get('capacity', 20))
        
        # 시험지에 제시된 배열 데이터
        # [19, 15, 29, 25, 33, 35, 49, 42, 50, 55, 62, 66, 77, 80]
        default_array = [19, 15, 29, 25, 33, 35, 49, 42, 50, 55, 62, 66, 77, 80]
        input_values = data.get('values', default_array)

        q = FixedQueue(capacity)
        steps = []

        # 1) 초기화 및 단계별 시뮬레이션 기록 생성
        steps.append(q.get_snapshot("1) 초기화", f"큐 사이즈 {capacity}로 초기화됨"))

        # 2) 위의 배열을 순서대로 push 하세요.
        for val in input_values:
            success, msg = q.push(val)
            steps.append(q.get_snapshot(f"2) Push({val})", msg))

        # 3) 현재의 개수는?
        length_val = q.get_length()
        steps.append(q.get_snapshot("3) 현재 데이터 개수 반환", f"현재 개수: {length_val}개"))

        # 4) 현재 상태는? (Full / Empty)
        is_f = q.is_full()
        is_e = q.is_empty()
        steps.append(q.get_snapshot("4) 상태 검사", f"Full: {is_f}, Empty: {is_e}"))

        # 5) 전면 데이터 확인
        front_val, front_msg = q.peek_front()
        steps.append(q.get_snapshot("5) 전면(Front) 데이터 확인", front_msg))

        # 6) 42 값의 위치(index)와 개수는?
        target_val_1 = 42
        idx_results = q.search_index(target_val_1)
        cnt_results = q.count_value(target_val_1)
        steps.append(q.get_snapshot(f"6) 값({target_val_1}) index 검색 및 개수", f"위치(Index): {idx_results}, 개수: {cnt_results}개"))

        # 7) 88 값의 존재 여부는?
        target_val_2 = 88
        exist_result = q.contains(target_val_2)
        steps.append(q.get_snapshot(f"7) 값({target_val_2}) 존재 여부 검사", f"존재 여부: {exist_result}"))

        # 8) 배열 전체를 출력 (Front부터 Rear까지)
        dump_data = q.dump_front_to_rear()
        steps.append(q.get_snapshot("8) Front부터 Rear까지 출력", f"출력 결과: {dump_data}"))

        complexity = {
            "time_complexity": "Push/Pop/Peek/Length: O(1), Search/Dump: O(N)",
            "space_complexity": f"O(N) 고정 크기 배열 (N={capacity})"
        }

        response_data = {
            "success": True,
            "total_steps": len(steps),
            "steps": steps,
            "complexity": complexity
        }
        return add_cors_headers(jsonify(response_data)), 200

    except Exception as e:
        return add_cors_headers(jsonify({"success": False, "error": str(e)})), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
