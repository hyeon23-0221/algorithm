import os
import re
import time
import math
import random
from typing import List, Optional, Dict, Any, Set
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="TeamFit & Smart Portfolio Hub API",
    version="1.0.0",
    description="Cloud Run microservice for Conditional Team Builder and Portfolio Gemini AI Assistant"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUT_OF_DOMAIN_REJECTION = "죄송합니다. 포토폴리오와 관련된 질문에만 답변할 수 있습니다."

# -------------------------------------------------------------
# Pydantic Models
# -------------------------------------------------------------
class ConstraintModel(BaseModel):
    id: Optional[str] = None
    type: str = Field(..., pattern="^(fixed|exclude)$")
    personA: str
    personB: str

class SolveTeamsRequest(BaseModel):
    participants: List[str]
    teamCount: int
    constraints: List[ConstraintModel] = []

class ChatRequest(BaseModel):
    prompt: str

# -------------------------------------------------------------
# Union-Find
# -------------------------------------------------------------
class UnionFind:
    def __init__(self, elements: List[str]):
        self.parent = {elem: elem for elem in elements}
        self.rank = {elem: 0 for elem in elements}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            return x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: str, y: str) -> bool:
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return False
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        return True

    def connected(self, x: str, y: str) -> bool:
        return self.find(x) == self.find(y)

    def get_groups(self) -> Dict[str, List[str]]:
        groups: Dict[str, List[str]] = {}
        for elem in list(self.parent.keys()):
            root = self.find(elem)
            groups.setdefault(root, []).append(elem)
        return groups

# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------
@app.get("/")
@app.get("/health")
def health_check():
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    return {
        "status": "healthy",
        "service": "teamfit-portfolio-cloudrun",
        "has_gemini_key": bool(gemini_key and not gemini_key.startswith("mock-")),
        "timestamp": time.time()
    }

@app.post("/solve")
def solve_teams_endpoint(req: SolveTeamsRequest):
    start_time = time.time()
    participants = [p.strip() for p in req.participants if p.strip()]
    N = len(participants)
    K = req.teamCount

    if K < 2:
        raise HTTPException(status_code=400, detail="조 개수는 최소 2개 이상이어야 합니다.")
    if N < K:
        raise HTTPException(status_code=400, detail=f"참여 인원({N}명)이 조 개수({K}개)보다 적습니다.")

    base_cap = N // K
    extra_count = N % K
    max_cap = math.ceil(N / K)
    target_capacities = [(base_cap + 1 if i < extra_count else base_cap) for i in range(K)]

    p_set = set(participants)
    valid_constraints = [c for c in req.constraints if c.personA in p_set and c.personB in p_set]
    fixed_rules = [c for c in valid_constraints if c.type == "fixed"]
    exclude_rules = [c for c in valid_constraints if c.type == "exclude"]

    # 1. Fixed Constraints via Union-Find
    uf = UnionFind(participants)
    for fc in fixed_rules:
        uf.union(fc.personA, fc.personB)

    # Conflict 1: Fixed vs Exclude collision
    for ec in exclude_rules:
        if uf.connected(ec.personA, ec.personB):
            return {
                "success": False,
                "error": f"고정 조건과 분리 조건 충돌: '{ec.personA}'와(과) '{ec.personB}'",
                "conflictDetails": {
                    "type": "fixed_exclude_collision",
                    "message": f"고정 조건과 분리 조건이 충돌합니다: '{ec.personA}'와(과) '{ec.personB}'"
                }
            }

    # 2. Meta Components
    groups = uf.get_groups()
    meta_components = []
    root_to_id = {}
    for idx, (root, members) in enumerate(groups.items()):
        if len(members) > max_cap:
            return {
                "success": False,
                "error": f"고정 그룹 인원({len(members)}명)이 조별 최대 정원({max_cap}명)을 초과합니다.",
                "conflictDetails": {
                    "type": "group_size_exceeded",
                    "message": f"고정 그룹 인원수({len(members)}명)가 조별 최대 수용 인원({max_cap}명)을 초과합니다."
                }
            }
        root_to_id[root] = idx
        meta_components.append({
            "id": idx,
            "root": root,
            "members": members,
            "size": len(members),
            "excludes": set()
        })

    for ec in exclude_rules:
        id_a = root_to_id[uf.find(ec.personA)]
        id_b = root_to_id[uf.find(ec.personB)]
        if id_a != id_b:
            meta_components[id_a]["excludes"].add(id_b)
            meta_components[id_b]["excludes"].add(id_a)

    # 3. Solver with Backtracking
    meta_components.sort(key=lambda m: m["size"], reverse=True)
    MAX_ITER = 2000
    TIMEOUT = 0.5
    iterations = 0
    solution_teams = None

    while iterations < MAX_ITER and (time.time() - start_time) < TIMEOUT:
        iterations += 1
        comps = list(meta_components)
        caps = list(target_capacities)
        random.shuffle(caps)

        assignments: List[List[int]] = [[] for _ in range(K)]
        sizes: List[int] = [0] * K
        excludes: List[Set[int]] = [set() for _ in range(K)]

        def backtrack(comp_idx: int) -> bool:
            if (time.time() - start_time) >= TIMEOUT:
                return False
            if comp_idx == len(comps):
                return True

            comp = comps[comp_idx]
            cand = [t for t in range(K) if sizes[t] + comp["size"] <= caps[t] and comp["id"] not in excludes[t]]
            random.shuffle(cand)

            for t in cand:
                assignments[t].append(comp["id"])
                sizes[t] += comp["size"]
                added = [ex for ex in comp["excludes"] if ex not in excludes[t]]
                for ex in added:
                    excludes[t].add(ex)

                if backtrack(comp_idx + 1):
                    return True

                assignments[t].pop()
                sizes[t] -= comp["size"]
                for ex in added:
                    excludes[t].remove(ex)

            return False

        if backtrack(0):
            comp_map = {m["id"]: m for m in meta_components}
            teams = []
            for i in range(K):
                members = []
                for cid in assignments[i]:
                    members.extend(comp_map[cid]["members"])
                random.shuffle(members)
                teams.append({
                    "id": i + 1,
                    "name": f"{i + 1}조",
                    "members": members
                })
            solution_teams = teams
            break

    elapsed_ms = int((time.time() - start_time) * 1000)

    if solution_teams:
        return {
            "success": True,
            "teams": solution_teams,
            "executionTimeMs": elapsed_ms,
            "iterationCount": iterations,
            "rulesApplied": {
                "fixedCount": len(fixed_rules),
                "excludeCount": len(exclude_rules)
            }
        }

    return {
        "success": False,
        "error": "탐색 시간 또는 한도 내에 조건을 만족하는 조 편성을 찾지 못했습니다.",
        "conflictDetails": {
            "type": "timeout_or_unsolvable",
            "message": "조건을 모두 만족하는 배치를 찾지 못했습니다. 제약 조건을 완화해 주세요."
        }
    }

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="질문 내용을 입력해 주세요.")
    if len(prompt) > 300:
        raise HTTPException(status_code=400, detail="질문은 최대 300자 이내로 입력해 주세요.")

    lower = prompt.lower()
    out_of_domain = [
        r"날씨", r"온도", r"수학", r"미적분", r"방정식",
        r"파이썬.*(풀어|짜줘|코드)", r"자바스크립트.*(풀어|짜줘)", r"숙제",
        r"정치", r"대통령", r"주식", r"비트코인", r"심심해", r"음식.*추천", r"맛집"
    ]
    for pattern in out_of_domain:
        if re.search(pattern, lower):
            return {
                "success": True,
                "message": OUT_OF_DOMAIN_REJECTION,
                "isRejection": True
            }

    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key and not api_key.startswith("mock-") and api_key != "your_gemini_api_key_here":
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=(
                    "당신은 '팀핏 & 스마트 포트폴리오 허브' 제작자 김인재의 포트폴리오 전용 AI 도우미입니다. "
                    "포트폴리오 프로젝트, 기술 스택, 트러블슈팅, 연락처 외의 질문에는 정확히 "
                    f"'{OUT_OF_DOMAIN_REJECTION}' 만 답변하십시오."
                )
            )
            resp = model.generate_content(prompt)
            text = (resp.text or "").strip()
            if any(k in text for k in ["포토폴리오", "포트폴리오와 관련된 질문", "관련된 질문에만"]):
                text = OUT_OF_DOMAIN_REJECTION
            return {
                "success": True,
                "message": text,
                "isRejection": text == OUT_OF_DOMAIN_REJECTION
            }
        except Exception:
            pass

    # Fallback response
    if any(k in lower for k in ["스택", "기술", "언어", "frontend", "backend"]):
        msg = "Next.js 14, TypeScript, Tailwind CSS, Python FastAPI, Cloud Run, Gemini Flash, Supabase"
    elif any(k in lower for k in ["조", "편성", "알고리즘", "팀핏"]):
        msg = "고정 조건은 Disjoint-Set(Union-Find)로 병합하고, 분리 조건 그래프 검증 후 균등 배분 백트래킹으로 최적 조를 산출합니다."
    elif any(k in lower for k in ["연락처", "이메일", "github"]):
        msg = "이메일: dev.injekim@gmail.com, GitHub: https://github.com/injekim-dev"
    else:
        msg = OUT_OF_DOMAIN_REJECTION

    return {
        "success": True,
        "message": msg,
        "isRejection": msg == OUT_OF_DOMAIN_REJECTION
    }
