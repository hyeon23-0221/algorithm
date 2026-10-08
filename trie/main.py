import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# 클라이언트 및 외부 환경에서의 CORS 요청 허용 설정
CORS(app)

class Node:
    """이진 검색 트리의 노드 클래스"""
    def __init__(self, key, value, left=None, right=None):
        self.key = key          # 비교/탐색 기준 키
        self.value = value      # 노드가 저장하는 값
        self.left = left        # 왼쪽 자식 노드 참조
        self.right = right      # 오른쪽 자식 노드 참조

    def to_dict(self):
        """트리 시각화를 위해 노드와 자식 관계를 딕셔너리 구조로 반환하는 메서드"""
        return {
            "key": self.key,
            "value": self.value,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }

class BinarySearchTree:
    """이진 검색 트리(BST) 클래스"""
    def __init__(self):
        self.root = None        # 트리의 루트 노드

    def search(self, key):
        """키에 해당하는 노드를 탐색 (단계별 경로 기록)"""
        steps = []
        ptr = self.root
        
        if ptr is None:
            steps.append({
                "action": "empty",
                "key": key,
                "message": "트리가 비어 있습니다."
            })
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
                    "message": f"[{key}] < [{ptr.key}] 이므로 왼쪽 자식 노드로 이동합니다."
                })
                ptr = ptr.left
            else:
                steps.append({
                    "action": "go_right",
                    "current_key": ptr.key,
                    "message": f"[{key}] > [{ptr.key}] 이므로 오른쪽 자식 노드로 이동합니다."
                })
                ptr = ptr.right

        steps.append({
            "action": "not_found",
            "key": key,
            "message": f"탐색 실패: 키 [{key}]가 트리에 존재하지 않습니다."
        })
        return steps, None

    def add(self, key, value):
        """트리에 새로운 (key, value) 노드 추가 (단계별 경로 기록)"""
        steps = []
        if self.root is None:
            self.root = Node(key, value)
            steps.append({
                "action": "insert_root",
                "key": key,
                "value": value,
                "message": f"트리가 비어 있어 키 [{key}]를 루트 노드로 삽입했습니다."
            })
            return steps, True

        ptr = self.root
        while True:
            steps.append({
                "action": "compare",
                "current_key": ptr.key,
                "target_key": key,
                "message": f"현재 노드 [{ptr.key}]와 삽입할 키 [{key}]를 비교합니다."
            })

            if key == ptr.key:
                # 이미 동일한 키가 있을 경우 값 업데이트
                ptr.value = value
                steps.append({
                    "action": "update",
                    "key": key,
                    "value": value,
                    "message": f"키 [{key}]가 이미 존재하므로 값을 '{value}'로 업데이트했습니다."
                })
                return steps, True
            elif key < ptr.key:
                if ptr.left is None:
                    ptr.left = Node(key, value)
                    steps.append({
                        "action": "insert_left",
                        "parent_key": ptr.key,
                        "key": key,
                        "value": value,
                        "message": f"노드 [{ptr.key}]의 왼쪽에 새로운 노드 [{key}]를 삽입했습니다."
                    })
                    return steps, True
                steps.append({
                    "action": "go_left",
                    "current_key": ptr.key,
                    "message": f"[{key}] < [{ptr.key}] 이므로 왼쪽으로 이동합니다."
                })
                ptr = ptr.left
            else:
                if ptr.right is None:
                    ptr.right = Node(key, value)
                    steps.append({
                        "action": "insert_right",
                        "parent_key": ptr.key,
                        "key": key,
                        "value": value,
                        "message": f"노드 [{ptr.key}]의 오른쪽에 새로운 노드 [{key}]를 삽입했습니다."
                    })
                    return steps, True
                steps.append({
                    "action": "go_right",
                    "current_key": ptr.key,
                    "message": f"[{key}] > [{ptr.key}] 이므로 오른쪽으로 이동합니다."
                })
                ptr = ptr.right

    def remove(self, key):
        """키에 해당하는 노드 삭제 (단계별 경로 및 재구조화 기록)"""
        steps = []
        ptr = self.root
        parent = None
        is_left_child = True

        # 1. 삭제할 노드 탐색
        while ptr is not None and ptr.key != key:
            parent = ptr
            steps.append({
                "action": "compare",
                "current_key": ptr.key,
                "target_key": key,
                "message": f"삭제 대상 탐색: 현재 노드 [{ptr.key}]와 키 [{key}] 비교"
            })
            if key < ptr.key:
                is_left_child = True
                ptr = ptr.left
            else:
                is_left_child = False
                ptr = ptr.right

        if ptr is None:
            steps.append({
                "action": "not_found",
                "key": key,
                "message": f"삭제 실패: 키 [{key}]를 찾지 못했습니다."
            })
            return steps, False

        steps.append({
            "action": "found_remove_target",
            "key": key,
            "message": f"삭제 대상 노드 [{key}]를 발견했습니다."
        })

        # 2. 삭제 노드의 자식 개수에 따른 처리
        # Case 1: 자식이 없는 노드(리프 노드) 삭제
        if ptr.left is None and ptr.right is None:
            if ptr == self.root:
                self.root = None
            elif is_left_child:
                parent.left = None
            else:
                parent.right = None
            steps.append({
                "action": "removed_leaf",
                "key": key,
                "message": f"리프 노드 [{key}]를 삭제했습니다."
            })

        # Case 2: 왼쪽 자식만 있는 경우
        elif ptr.right is None:
            if ptr == self.root:
                self.root = ptr.left
            elif is_left_child:
                parent.left = ptr.left
            else:
                parent.right = ptr.left
            steps.append({
                "action": "removed_with_left_child",
                "key": key,
                "message": f"노드 [{key}]를 삭제하고, 왼쪽 자식을 부모 노드에 연결했습니다."
            })

        # Case 2: 오른쪽 자식만 있는 경우
        elif ptr.left is None:
            if ptr == self.root:
                self.root = ptr.right
            elif is_left_child:
                parent.left = ptr.right
            else:
                parent.right = ptr.right
            steps.append({
                "action": "removed_with_right_child",
                "key": key,
                "message": f"노드 [{key}]를 삭제하고, 오른쪽 자식을 부모 노드에 연결했습니다."
            })

        # Case 3: 자식이 둘 다 있는 경우 (오른쪽 서브트리에서 최소값 노드로 대체)
        else:
            parent_of_succ = ptr
            succ = ptr.right
            while succ.left is not None:
                parent_of_succ = succ
                succ = succ.left

            steps.append({
                "action": "find_successor",
                "successor_key": succ.key,
                "message": f"오른쪽 서브트리의 최소값 노드 [{succ.key}]를 대체 노드(Successor)로 선택합니다."
            })

            # 대체 노드의 값을 삭제 대상 노드에 복사
            ptr.key = succ.key
            ptr.value = succ.value

            # 대체 노드 제거
            if parent_of_succ.left == succ:
                parent_of_succ.left = succ.right
            else:
                parent_of_succ.right = succ.right

            steps.append({
                "action": "replaced_successor",
                "key": key,
                "replaced_key": succ.key,
                "message": f"노드 [{key}] 위치를 대체 노드 [{succ.key}]의 값으로 덮어쓰고 기존 위치를 정리했습니다."
            })

        return steps, True

    def min_key(self):
        """트리에서 가장 작은 키(가장 왼쪽 노드) 탐색"""
        steps = []
        if self.root is None:
            steps.append({"action": "empty", "message": "트리가 비어 있습니다."})
            return steps, None

        ptr = self.root
        while ptr.left is not None:
            steps.append({
                "action": "go_left",
                "current_key": ptr.key,
                "message": f"최소값 탐색: 현재 노드 [{ptr.key}]에서 왼쪽 자식으로 이동합니다."
            })
            ptr = ptr.left

        steps.append({
            "action": "found_min",
            "current_key": ptr.key,
            "value": ptr.value,
            "message": f"최소 키 노드 발견! 키: [{ptr.key}], 값: '{ptr.value}'"
        })
        return steps, {"key": ptr.key, "value": ptr.value}

    def max_key(self):
        """트리에서 가장 큰 키(가장 오른쪽 노드) 탐색"""
        steps = []
        if self.root is None:
            steps.append({"action": "empty", "message": "트리가 비어 있습니다."})
            return steps, None

        ptr = self.root
        while ptr.right is not None:
            steps.append({
                "action": "go_right",
                "current_key": ptr.key,
                "message": f"최대값 탐색: 현재 노드 [{ptr.key}]에서 오른쪽 자식으로 이동합니다."
            })
            ptr = ptr.right

        steps.append({
            "action": "found_max",
            "current_key": ptr.key,
            "value": ptr.value,
            "message": f"최대 키 노드 발견! 키: [{ptr.key}], 값: '{ptr.value}'"
        })
        return steps, {"key": ptr.key, "value": ptr.value}

    def dump(self):
        """트리의 루트 노드 구조를 반환 (덤프 기능)"""
        return self.root.to_dict() if self.root else None


# 전역 이진 검색 트리 인스턴스 초기화
bst = BinarySearchTree()

# 기본 샘플 데이터 초기화
initial_items = [
    (50, "중앙"), (30, "왼쪽1"), (70, "오른쪽1"),
    (20, "왼쪽2"), (40, "왼쪽3"), (60, "오른쪽2"), (80, "오른쪽3")
]
for k, v in initial_items:
    bst.add(k, v)


@app.route('/bst', methods=['POST'])
def handle_bst():
    """
    클라이언트 요청 처리 엔드포인트
    action: 'init', 'add', 'remove', 'search', 'dump', 'min_key', 'max_key'
    """
    global bst
    try:
        data = request.get_json() or {}
        action = data.get('action', 'dump')
        key = data.get('key')
        value = data.get('value')

        if key is not None and key != '':
            key = int(key)

        steps = []
        result_val = None
        success = True

        if action == 'init':
            # 1. 트리 초기화 (init)
            bst = BinarySearchTree()
            steps.append({
                "action": "init",
                "message": "이진 검색 트리가 새로 초기화되었습니다."
            })

        elif action == 'add':
            # 2. 노드 삽입 (add)
            if key is None or not value:
                return jsonify({"success": False, "error": "숫자 Key와 Value를 모두 입력해주세요."}), 400
            steps, success = bst.add(key, value)

        elif action == 'search':
            # 3. 노드 검색 (search)
            if key is None:
                return jsonify({"success": False, "error": "검색할 숫자 Key를 입력해주세요."}), 400
            steps, result_val = bst.search(key)

        elif action == 'remove':
            # 4. 노드 삭제 (remove)
            if key is None:
                return jsonify({"success": False, "error": "삭제할 숫자 Key를 입력해주세요."}), 400
            steps, success = bst.remove(key)

        elif action == 'min_key':
            # 5. 최소 키 검색 (min_key)
            steps, result_val = bst.min_key()

        elif action == 'max_key':
            # 6. 최대 키 검색 (max_key)
            steps, result_val = bst.max_key()

        elif action == 'dump':
            # 7. 전체 덤프 (dump)
            steps.append({
                "action": "dump",
                "message": "이진 검색 트리의 전체 계층 구조를 덤프합니다."
            })

        else:
            return jsonify({"success": False, "error": f"지원하지 않는 동작입니다: {action}"}), 400

        # 복잡도 정보
        complexity = {
            "time_complexity": "평균 O(log N) / 최악 O(N)",
            "space_complexity": "O(N)",
            "description": "균형 트리에서는 O(log N)으로 빠른 탐색/삽입/삭제가 가능하며, 한쪽으로 치우친 편향 트리에서는 O(N)까지 증가할 수 있습니다."
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
    """서버 상태 확인용 헬스체크"""
    return "Binary Search Tree Cloud Run Server is running!", 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
