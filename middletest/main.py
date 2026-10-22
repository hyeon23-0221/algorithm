import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# CORS 헤더 추가 함수 (Apps Script 및 브라우저 요청 허용)
def build_cors_preflight_response():
    response = jsonify({'status': 'CORS Preflight OK'})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response, 200

def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

class FixedQueue:
    """고정 길이 큐 알고리즘 클래스"""
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = [None] * capacity  # 고정된 크기의 배열 생성
        self.front = 0                 # Dequeue 위치 (Front)
        self.rear = 0                  # Enqueue 위치 (Rear)
        self.size = 0                  # 현재 요소 개수

    def is_full(self):
        return self.size == self.capacity

    def is_empty(self):
        return self.size == 0

    def enqueue(self, item):
        if self.is_full():
            return False, "Overflow: Queue is Full"
        self.queue[self.rear] = item
        self.rear = (self.rear + 1) % self.capacity  # 원형 큐 인덱스 계산
        self.size += 1
        return True, f"Enqueued: {item}"

    def dequeue(self):
        if self.is_empty():
            return False, "Underflow: Queue is Empty", None
        item = self.queue[self.front]
        self.queue[self.front] = None
        self.front = (self.front + 1) % self.capacity  # 원형 큐 인덱스 계산
        self.size -= 1
        return True, f"Dequeued: {item}", item

    def get_snapshot(self, action_desc, status_msg):
        """시각화를 위해 현재 큐의 내부 상태를 스냅샷으로 저장"""
        return {
            "queue": list(self.queue),
            "front": self.front,
            "rear": self.rear,
            "size": self.size,
            "capacity": self.capacity,
            "action": action_desc,
            "status": status_msg
        }

@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def handle_queue():
    # CORS Preflight 처리
    if request.method == 'OPTIONS':
        return build_cors_preflight_response()

    # GET 요청 테스트용
    if request.method == 'GET':
        resp = jsonify({"status": "Google Cloud Run Fixed-length Queue Server Running"})
        return add_cors_headers(resp), 200

    # POST 요청 처리
    try:
        data = request.get_json(force=True) if request.is_json else request.form
        capacity = int(data.get('capacity', 5))
        operations = data.get('operations', []) # 예: [{"op": "enqueue", "val": "A"}, {"op": "dequeue"}]

        # 기본 시뮬레이션 데이터가 없으면 예시 데이터 생성
        if not operations:
            operations = [
                {"op": "enqueue", "val": "Data-A"},
                {"op": "enqueue", "val": "Data-B"},
                {"op": "enqueue", "val": "Data-C"},
                {"op": "dequeue", "val": None},
                {"op": "enqueue", "val": "Data-D"},
                {"op": "enqueue", "val": "Data-E"},
                {"op": "enqueue", "val": "Data-F"}, # Overflow 테스트
                {"op": "dequeue", "val": None},
            ]

        q = FixedQueue(capacity)
        steps = []
        
        # Initial State
        steps.append(q.get_snapshot("Initialize", f"Queue initialized with capacity {capacity}"))

        # 알고리즘 단계별 수행
        for op in operations:
            action_type = op.get('op')
            val = op.get('val')

            if action_type == 'enqueue':
                success, msg = q.enqueue(val)
                steps.append(q.get_snapshot(f"Enqueue({val})", msg))
            elif action_type == 'dequeue':
                success, msg, _ = q.dequeue()
                steps.append(q.get_snapshot("Dequeue()", msg))

        # 복잡도 정보
        complexity = {
            "time_complexity": "O(1) for Enqueue & Dequeue",
            "space_complexity": f"O(N) where N = capacity ({capacity})"
        }

        result = jsonify({
            "success": True,
            "total_steps": len(steps),
            "steps": steps,
            "complexity": complexity
        })
        return add_cors_headers(result), 200

    except Exception as e:
        err_resp = jsonify({"success": False, "error": str(e)})
        return add_cors_headers(err_resp), 400

if __name__ == "__main__":
    # Cloud Run에서 할당하는 PORT 환경 변수 수신
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
