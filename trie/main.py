import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# 외부 및 클라이언트 환경과의 교차 출처 리소스 공유(CORS) 허용 설정
CORS(app)

class Node:
    """이진 검색 트리(BST)의 개별 노드 클래스"""
    def __init__(self, key, value, left=None, right=None):
        self.key = key          # 탐색 및 정렬 기준 키 (숫자)
        self.value = value      # 노드가 품고 있는 데이터 값
        self.left = left        # 왼쪽 자식 노드 참조
        self.right = right      # 오른쪽 자식 노드 참조

    def to_dict(self):
        """웹 클라이언트 시각화를 위해 계층 구조를 딕셔너리로 변환"""
        return {
            "key": self.key,
            "value": self.value,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }

class binarySearchTree:
    """이진 검색 트리(Binary Search Tree) 관리 클래스"""
    def __init__(self):
        self.root = None        # 트리의 루트(Root) 노드

    def search(self, key):
        """키 값을 이용해 노드를 탐색하고 탐색 과정을 단계별로 기록"""
        steps = []
        ptr = self.root
        
        if ptr is None:
            steps.append({"action": "empty", "message": "트리가 비어 있습니다."})
            return steps, None

        while ptr is not None:
            steps.append({
                "action": "compare",
                "current_key": ptr.key,
                "target_key": key,
                "message": f"현재 노드 [{ptr.key}]와 찾을 키 [{key}]를 비교합니다."
            })

            if key == ptr.key:
                steps.append({
                    "action": "found",
                    "current_key": ptr.key,
                    "value": ptr.value,
                    "message": f"성공! 키 [{key}]를 찾았습니다. 값: '{ptr.value}'"
                })
                return steps, ptr.value
            elif key < ptr.key:
                steps.append({
                    "action": "go_left",
                    "current_key": ptr.key,
                    "message": f"[{key}] < [{ptr.key}] 이므로 왼쪽 자식으로 이동합니다."
                })
                ptr = ptr.left
            else:
                steps.append({
                    "action": "go_right",
                    "current_key": ptr.key,
                    "message": f"[{key}] > [{ptr.key}] 이므로 오른쪽 자식으로 이동합니다."
                })
                ptr = ptr.right

        steps.append({"action": "not_found", "message": f"탐색 실패: 키 [{key}]가 존재하지 않습니다."})
        return steps, None

    def add(self, key, value):
        """트리에 새로운 키와 값을 삽입하고 과정을 단계별로 기록"""
        steps = []
        if self.root is None:
            self.root = Node(key, value)
            steps.append({"action": "insert_root", "key": key, "message": f"트리가 비어 있어 키 [{key}]를 루트 노드로 삽입했습니다."})
            return steps, True

        ptr = self.root
        while True:
            steps.append({"action": "compare", "current_key": ptr.key, "target_key": key, "message": f"현재 노드 [{ptr.key}]와 삽입할 키 [{key}]를 비교합니다."})

            if key == ptr.key:
                ptr.value = value
                steps.append({"action": "update", "key": key, "message": f"키 [{key}]가 이미 존재하므로 값을 '{value}'로 갱신했습니다."})
                return steps, True
            elif key < ptr.key:
                if ptr.left is None:
                    ptr.left = Node(key, value)
                    steps.append({"action": "insert_left", "key": key, "message": f"노드 [{ptr.key}]의 왼쪽에 키 [{key}]를 삽입했습니다."})
                    return steps, True
                ptr = ptr.left
            else:
                if ptr.right is None:
                    ptr.right = Node(key, value)
                    steps.append({"action": "insert_right", "key": key, "message": f"노드 [{ptr.key}]의 오른쪽에 키 [{key}]를 삽입했습니다."})
                    return steps, True
                ptr = ptr.right

    def remove(self, key):
        """키에 해당하는 노드를 삭제하고 트리 구조를 재조정"""
        steps = []
        ptr = self.root
        parent = None
        is_left_child = True

        while ptr is not None and ptr.key != key:
            parent = ptr
            if key < ptr.key:
                is_left_child = True
                ptr = ptr.left
            else:
                is_left_child = False
                ptr = ptr.right

        if ptr is None:
            steps.append({"action": "not_found", "message": f"삭제 실패: 키 [{key}]가 존재하지 않습니다."})
            return steps, False

        # 자식이 없는 경우 (리프 노드)
        if ptr.left is None and ptr.right is None:
            if ptr == self.root: self.root = None
            elif is_left_child: parent.left = None
            else: parent.right = None
        # 왼쪽 자만 있는 경우
        elif ptr.right is None:
            if ptr == self.root: self.root = ptr.left
            elif is_left_child: parent.left = ptr.left
            else: parent.right = ptr.left
        # 오른쪽 자만 있는 경우
        elif ptr.left is None:
            if ptr == self.root: self.root = ptr.right
            elif is_left_child: parent.left = ptr.right
            else: parent.right = ptr.right
        # 자식이 둘 다 있는 경우 (오른쪽 서브트리의 최소값으로 대체)
        else:
            parent_of_succ = ptr
            succ = ptr.right
            while succ.left is not None:
                parent_of_succ = succ
                succ = succ.left
            
            ptr.key = succ.key
            ptr.value = succ.value
            if parent_of_succ.left == succ: parent_of_succ.left = succ.right
            else: parent_of_succ.right = succ.right

        steps.append({"action": "removed", "key": key, "message": f"성공적으로 키 [{key}] 노드를 삭제했습니다."})
        return steps, True

    def min_key(self):
        """트리 내에서 가장 작은 키 값을 탐색"""
        steps = []
        if self.root is None:
            steps.append({"action": "empty", "message": "트리가 비어 있습니다."})
            return steps, None
        
        ptr = self.root
        while ptr.left is not None:
            ptr = ptr.left
        steps.append({"action": "found_min", "message": f"최소 키 발견: [{ptr.key}] (값: {ptr.value})"})
        return steps, {"key": ptr.key, "value": ptr.value}

    def max_key(self):
        """트리 내에서 가장 큰 키 값을 탐색"""
        steps = []
        if self.root is None:
            steps.append({"action": "empty", "message": "트리가 비어 있습니다."})
            return steps, None
        
        ptr = self.root
        while ptr.right is not None:
            ptr = ptr.right
        steps.append({"action": "found_max", "message": f"최대 키 발견: [{ptr.key}] (값: {ptr.value})"})
        return steps, {"key": ptr.key, "value": ptr.value}

    def dump(self):
        """트리의 전체 구조를 반환"""
        return self.root.to_dict() if self.root else None


# 전역 이진 검색 트리 인스턴스
bst = binarySearchTree()

# 초기 샘플 데이터 적재
for k, v in [(50, "root"), (30, "left"), (70, "right")]:
    bst.add(k, v)


@app.route('/bst', methods=['POST'])
def handle_bst():
    """클라이언트 요청 처리 엔드포인트"""
    global bst
    try:
        data = request.get_json() or {}
        action = data.get('action', 'dump')
        key = data.get('key')
        value = data.get('value')
        if key is not None and key != '': key = int(key)

        steps, result_val, success = [], None, True

        if action == 'init':
            bst = binarySearchTree()
            steps.append({"action": "init", "message": "이진 검색 트리가 초기화되었습니다."})
        elif action == 'add':
            steps, success = bst.add(key, value)
        elif action == 'search':
            steps, result_val = bst.search(key)
        elif action == 'remove':
            steps, success = bst.remove(key)
        elif action == 'min_key':
            steps, result_val = bst.min_key()
        elif action == 'max_key':
            steps, result_val = bst.max_key()
        elif action == 'dump':
            steps.append({"action": "dump", "message": "트리 구조를 덤프합니다."})
        else:
            return jsonify({"success": False, "error": "지원하지 않는 명령입니다."}), 400

        complexity = {
            "time_complexity": "평균 O(log N) / 최악 O(N)",
            "space_complexity": "O(N)",
            "description": "균형 잡힌 트리에서는 로그 시간 복잡도로 동작합니다."
        }

        return jsonify({
            "success": success,
            "action": action,
            "steps": steps,
            "result_value": result_val,
            "dump": bst.dump(),
            "complexity": complexity
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/', methods=['GET'])
def health_check():
    return "BST Cloud Run Server is running!", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
