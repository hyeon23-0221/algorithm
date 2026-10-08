import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# 클라이언트(GAS 및 브라우저) 교차 출처 리소스 공유(CORS) 허용 설정
CORS(app)

class Node:
    """해시 테이블 체이닝을 위한 노드 클래스"""
    def __init__(self, key, value, next_node=None):
        self.key = key          # 키 (문자열 또는 숫자)
        self.value = value      # 값
        self.next = next_node   # 다음 노드 포인터

class ChainedHash:
    """체이닝 방식의 해시 테이블 클래스"""
    def __init__(self, capacity=13):
        self.capacity = capacity              # 해시 테이블 크기 (소수 권장)
        self.table = [None] * self.capacity   # 버킷 배열

    def _hash_value(self, key):
        """키의 해시값(버킷 인덱스)을 계산"""
        if isinstance(key, int):
            return key % self.capacity
        return sum(ord(c) for c in str(key)) % self.capacity

    def add(self, key, value):
        """키와 값을 해시 테이블에 추가 (단계 기록)"""
        steps = []
        hash_idx = self._hash_value(key)
        steps.append({
            "action": "hash_calc",
            "bucket": hash_idx,
            "message": f"키 '{key}'의 해시값(버킷 인덱스)은 {hash_idx}입니다."
        })
        
        ptr = self.table[hash_idx]
        while ptr is not None:
            if ptr.key == key:
                # 이미 키가 존재하는 경우 값 업데이트
                ptr.value = value
                steps.append({
                    "action": "update",
                    "bucket": hash_idx,
                    "key": key,
                    "value": value,
                    "message": f"버킷 [{hash_idx}]에서 기존 키 '{key}'를 발견하여 값을 '{value}'로 업데이트했습니다."
                })
                return steps, True
            ptr = ptr.next
            
        # 새로운 노드를 체인의 맨 앞에 추가
        temp = Node(key, value, self.table[hash_idx])
        self.table[hash_idx] = temp
        steps.append({
            "action": "insert",
            "bucket": hash_idx,
            "key": key,
            "value": value,
            "message": f"버킷 [{hash_idx}]의 체인 앞에 노드(Key: '{key}', Value: '{value}')를 추가했습니다."
        })
        return steps, True

    def search(self, key):
        """키를 이용해 해시 테이블에서 값 탐색 (단계 기록)"""
        steps = []
        hash_idx = self._hash_value(key)
        steps.append({
            "action": "hash_calc",
            "bucket": hash_idx,
            "message": f"키 '{key}'의 해시값은 {hash_idx}입니다. 버킷 [{hash_idx}]의 체인을 탐색합니다."
        })
        
        ptr = self.table[hash_idx]
        chain_pos = 0
        while ptr is not None:
            steps.append({
                "action": "compare",
                "bucket": hash_idx,
                "chain_pos": chain_pos,
                "current_key": ptr.key,
                "target_key": key,
                "message": f"버킷 [{hash_idx}] 노드 {chain_pos}: 키 '{ptr.key}'와 찾는 키 '{key}'를 비교합니다."
            })
            if ptr.key == key:
                steps.append({
                    "action": "found",
                    "bucket": hash_idx,
                    "chain_pos": chain_pos,
                    "key": ptr.key,
                    "value": ptr.value,
                    "message": f"성공! 키 '{key}'를 찾았습니다. 값: '{ptr.value}'"
                })
                return steps, ptr.value
            ptr = ptr.next
            chain_pos += 1

        steps.append({
            "action": "not_found",
            "bucket": hash_idx,
            "key": key,
            "message": f"탐색 실패: 버킷 [{hash_idx}]의 체인 끝까지 탐색했으나 키 '{key}'가 존재하지 않습니다."
        })
        return steps, None

    def remove(self, key):
        """키에 해당하는 노드를 해시 테이블에서 삭제 (단계 기록)"""
        steps = []
        hash_idx = self._hash_value(key)
        steps.append({
            "action": "hash_calc",
            "bucket": hash_idx,
            "message": f"키 '{key}'의 해시값은 {hash_idx}입니다. 버킷 [{hash_idx}]에서 삭제할 노드를 찾습니다."
        })

        ptr = self.table[hash_idx]
        pptr = None # 이전 노드
        chain_pos = 0

        while ptr is not None:
            if ptr.key == key:
                if pptr is None:
                    # 체인의 첫 번째 노드 삭제
                    self.table[hash_idx] = ptr.next
                else:
                    # 중간 또는 끝 노드 삭제
                    pptr.next = ptr.next
                steps.append({
                    "action": "removed",
                    "bucket": hash_idx,
                    "key": key,
                    "message": f"성공! 버킷 [{hash_idx}]의 노드(Key: '{key}')를 삭제했습니다."
                })
                return steps, True
            pptr = ptr
            ptr = ptr.next
            chain_pos += 1

        steps.append({
            "action": "not_found",
            "bucket": hash_idx,
            "key": key,
            "message": f"삭제 실패: 버킷 [{hash_idx}]에 키 '{key}'가 존재하지 않습니다."
        })
        return steps, False

    def dump(self):
        """전체 해시 테이블 구조(버킷 및 체인)를 상태 객체로 반환"""
        dump_data = []
        for i in range(self.capacity):
            chain = []
            ptr = self.table[i]
            while ptr is not None:
                chain.append({"key": ptr.key, "value": ptr.value})
                ptr = ptr.next
            dump_data.append({"bucket": i, "chain": chain})
        return dump_data


# 전역 해시 테이블 인스턴스 (초기 크기 7)
hash_table = ChainedHash(capacity=7)

# 기본 샘플 데이터 초기화
initial_items = [("apple", "사과"), ("banana", "바나나"), ("cherry", "체리"), ("grape", "포도")]
for k, v in initial_items:
    hash_table.add(k, v)


@app.route('/hash', methods=['POST'])
def handle_hash():
    """
    클라이언트 요청 처리 엔드포인트
    action: 'init', 'add', 'remove', 'search', 'dump', 'hash_value'
    """
    global hash_table
    try:
        data = request.get_json() or {}
        action = data.get('action', 'dump')
        key = data.get('key')
        value = data.get('value')
        capacity = data.get('capacity', 7)

        steps = []
        result_val = None
        success = True

        if action == 'init':
            # 1. 테이블 재초기화 (init)
            hash_table = ChainedHash(capacity=int(capacity))
            steps.append({
                "action": "init",
                "message": f"크기 {capacity}의 새로운 해시 테이블이 초기화되었습니다."
            })

        elif action == 'hash_value':
            # 2. 해시값 계산 (hash_value)
            h_val = hash_table._hash_value(key)
            steps.append({
                "action": "hash_value",
                "bucket": h_val,
                "message": f"키 '{key}'의 해시값(버킷 인덱스): {h_val}"
            })
            result_val = h_val

        elif action == 'add':
            # 3. 데이터 추가 (add)
            if not key or not value:
                return jsonify({"success": False, "error": "Key와 Value를 모두 입력해주세요."}), 400
            steps, success = hash_table.add(key, value)

        elif action == 'search':
            # 4. 데이터 검색 (search)
            if not key:
                return jsonify({"success": False, "error": "검색할 Key를 입력해주세요."}), 400
            steps, result_val = hash_table.search(key)

        elif action == 'remove':
            # 5. 데이터 삭제 (remove)
            if not key:
                return jsonify({"success": False, "error": "삭제할 Key를 입력해주세요."}), 400
            steps, success = hash_table.remove(key)

        elif action == 'dump':
            # 6. 전체 구조 덤프 (dump)
            steps.append({
                "action": "dump",
                "message": "해시 테이블의 전체 덤프 상태를 출력합니다."
            })

        else:
            return jsonify({"success": False, "error": f"지원하지 않는 동작입니다: {action}"}), 400

        # 복잡도 정보
        complexity = {
            "time_complexity": "O(1) [최악 O(N)]",
            "space_complexity": "O(N + M)",
            "description": "해시 함수를 통해 평균 O(1) 시간 복잡도로 탐색/추가/삭제를 수행합니다."
        }

        return jsonify({
            "success": success,
            "action": action,
            "steps": steps,
            "result_value": result_val,
            "dump": hash_table.dump(),
            "complexity": complexity
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/', methods=['GET'])
def health_check():
    """헬스체크 엔드포인트"""
    return "Hash Search Cloud Run Server is running!", 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
