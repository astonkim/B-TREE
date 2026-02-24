# B-TREE 구현

## 1. Functions

### Insertion & Searching
- input.csv에 있는 값들을 모두 읽어 삽입 연산 수행
- input.csv에 있는 100만개의 key들을 모두 search하여 그 value를 새로운 파일에 입력 한 뒤, 새 파일을 원래의 input.csv파일과 비교

### Deletion
- input.csv에 있는 100만개 key-value 쌍들 중 절반에 대하여 삭제 연산 수행
    - 삭제 대상인 key-value 쌍은 delete.csv에 제시되어 있음
- input.csv에 있는 100만개의 key들을 모두 search하여 그 value를 새로운 파일에 입력한 뒤, 새 파일을 delete_compare.csv 파일과 비교
    - 기존의 데이터셋에서 삭제된 value들은 생성된 새 파일 내에 "없는 값"(e.g. N/A, NF)이라고 출력되어야 함

## 2. Performance Evaluation
1) 프로그램 실행하면 어느 연산을 수행할 것인지 선택(ex: 1.insertion 2.deletion. 3.quit)
2) 숫자 1을 입력하면 insert할 파일 이름을 입력하는 화면이 나타나고, 삽입할 정보가 담긴 파일 이름 입력
3) 파일이름 입력하면 insertion, search, compare를 자동으로 수행하고 결과 화면 출력
4) 3단계의 동작 종료 후 1단계의 화면이 다시 나타나고, 숫자 2를 입력하면 delete할 파일 이름을 입력하는 화면이 나타나고, 삭제 정보가 담긴 파일 이름 입력
5) 파일이름 입력하면 deletion, search, compare를 자동으로 수행하고 결과 화면 출력
6) 5단계의 동작 종료 후 1단계의 화면이 다시 나타나고, 3번을 입력하여 프로그램 종료

## 3. Dev Environment
- Python 3.10.18
- OS: MacOS 26.2 Tahoe
- IDE: Visual Studio Code
- Memory: 64GB
- CPU: Apple M4 Pro

## 4. Structure

```
B-TREE/
├── btree.py              # 기본 구현 (linear search)
├── btree_optim.py        # 최적화 버전 (bisect + __slots__)
├── input.csv             # 원본 데이터셋 1 (100만)
├── input22.csv           # 원본 데이터셋 2 (100만)
├── delete.csv            # 삭제 대상 (input.csv용, 50만)
├── delete2.csv           # 삭제 대상 (input22.csv용, ~50만)
├── delete_compare.csv    # 삭제 후 비교용 (input.csv용)
├── delete_compare2.csv   # 삭제 후 비교용 (input22.csv용)
├── search_result.csv     # 검색 결과 출력용
└── delete_result.csv     # 삭제 후 검색 결과 출력용
```

## 5. 구현 순서
1) B-Tree Node 클래스 구현
    - keys, vals, kids, leaf 속성 정의
2) B-Tree 클래스 구현
    - 삽입 연산 (insert)
    - 검색 연산 (search)
    - 삭제 연산 (delete)
3) 파일 I/O 함수 구현
4) 성능 평가 및 비교 함수 구현
5) main() - 메인 함수 구현 및 사용자 인터페이스 작성 (메뉴 루프)

## 6. B-Tree 정리

### 구현 설정 (t = minimum degree)

| 설정 | 값 |
|------|-----|
| Minimum degree (t) | 100 |
| 노드당 최소 키 (non-root) | t-1 = 99 |
| 노드당 최대 키 | 2t-1 = 199 |
| 노드당 최소 자식 (non-root) | t = 100 |
| 노드당 최대 자식 | 2t = 200 |

### 기본 속성 (B-Tree invariants)
| 속성 | 규칙 |
|------|------|
| 키 개수 (루트) | 1 ≤ keys ≤ 2t-1 |
| 키 개수 (내부/리프) | t-1 ≤ keys ≤ 2t-1 |
| 자식 개수 (내부 노드) | t ≤ children ≤ 2t |
| 정렬 | 각 노드 내 키는 오름차순 |
| 균형 | 모든 리프 노드는 같은 깊이 |

### Search
**Search(node, key):**
1. 현재 노드에서 key를 찾음
2. node가 none이면 "not found" 반환
3. node의 key list에서 key 위치 i 찾음
4. key가 node.keys[i]와 같으면 해당 value 반환
5. key가 node.keys[i]보다 작은 첫 번째 i 찾아 자식 node.kids[i]로 재귀 탐색
6. key가 모든 keys보다 크면 마지막 자식 node.kids[len(keys)]로 재귀 탐색

### Insertion
**"삽입은 항상 leaf node에서 시작, Overflow 시 부모 node로 split"**

**Insert(tree, key, value):**
1. 루트 node가 full인지 확인 (키 개수 == 2t-1)
2. tree가 비어있으면 새 루트 node 생성, key 삽입
3. 적절한 leaf node 찾기 위해 재귀적으로 이동 (각 단계에서 key와 현재 node의 keys 비교)
4. leaf node에 key-value 쌍 삽입 (오름차순 정렬 유지)
5. node의 key 개수가 2t-1 초과 시 split 수행

**"node가 Overflow되면 (key 개수 > 2t-1)"**
**Split(node):**
1. 중간 키(median key, index = t-1)를 찾음
2. node를 두 개의 node로 분할 (왼쪽 node(median 이전 keys)와 오른쪽 node(median 이후 keys))
3. median key를 부모 node로 올림 (승격)
4. 부모 node가 full이면(Overflow) 재귀적으로 split 수행
5. root가 split되면 새 root node 생성, tree 높이 증가

### Deletion

**Deletion(node, key):**
1. key 탐색
2. key가 leaf node에 있으면
    - key 삭제
    - underflow(키 개수 < t-1) 발생 시 형제 노드에서 키 빌리기(Borrow) 또는 병합(Merge) 수행
3. key가 내부 노드에 있으면
    - key의 predecessor(왼쪽 서브트리에서 가장 큰 키) 또는 successor(오른쪽 서브트리에서 가장 작은 키)로 대체
    - 해당 key를 leaf node에서 재귀적으로 삭제
4. 재균형이 루트까지 전파될 수 있음
    - 루트가 비어있으면 자식이 새 루트가 됨, 트리 높이 감소

## 7. 알고리즘 성능 최적화

### 7.1 최적화 기법

| 기법 | 설명 | 효과 |
|------|------|------|
| `__slots__` | Node class memory layout 최적화 | 메모리 ~5% 절감 |
| `bisect_left` | linear search → binary search | node 내 탐색 O(n) → O(log n) |
| 반복문 전환 | search()에서 재귀 → while 루프 | 함수 호출 overhead 제거 |

---

### 7.2 Search & Insertion 성능 비교

#### input.csv (1,000,000 records)

| 버전 | Insertion | Search | 메모리(Insert) | 메모리(Search) |
|------|-----------|--------|----------------|----------------|
| 기본 구현 | 1.28s | 6.90s | 18.43 MB | 61.46 MB |
| 최적화 버전 | 1.18s | 0.57s | 17.58 MB | 61.46 MB |
| **개선율** | **1.08x** | **12.1x** | **4.6% ↓** | - |

[기본 구현]

<img width="481" height="392" alt="Image" src="https://github.com/user-attachments/assets/32ad3b6a-12b1-43a1-9c46-72dc33dc7722" />

[최적화 버전]

<img width="469" height="397" alt="Image" src="https://github.com/user-attachments/assets/4efa1bac-fc13-44d1-be04-499aefb3a69d" />

#### input22.csv (1,000,000 records)

| 버전 | Insertion | Search | 메모리(Insert) | 메모리(Search) |
|------|-----------|--------|----------------|----------------|
| 기본 구현 | 7.61s | 10.06s | 18.78 MB | 61.46 MB |
| 최적화 버전 | 6.84s | 1.33s | 18.17 MB | 61.46 MB |
| **개선율** | **1.11x** | **7.6x** | **3.2% ↓** | - |

[기본 구현]

<img width="483" height="389" alt="Image" src="https://github.com/user-attachments/assets/18de64cc-f8ab-4eda-ab9b-f2d8b4d2bfa8" />

[최적화 버전]

<img width="496" height="385" alt="Image" src="https://github.com/user-attachments/assets/1c063de4-05d0-407e-8d4d-17d0e07d5b09" />

---

### 7.3 Deletion 성능 비교

#### delete.csv (500,000 records)

| 버전 | Deletion | Search | 메모리(Delete) | 메모리(Search) |
|------|----------|--------|----------------|----------------|
| 기본 구현 | 3.96s | 6.59s | 9.07 MB | 61.36 MB |
| 최적화 버전 | 0.49s | 0.53s | 9.07 MB | 61.36 MB |
| **개선율** | **8.1x** | **12.4x** | - | - |

[기본 구현]

<img width="667" height="418" alt="Image" src="https://github.com/user-attachments/assets/2455298a-e5a2-4635-b540-c64a2b79f00d" />

[최적화 버전]

<img width="664" height="412" alt="Image" src="https://github.com/user-attachments/assets/fa763db3-892d-4a48-9906-d4ab37de7c7f" />

#### delete2.csv (499,724 records)

| 버전 | Deletion | Search | 메모리(Delete) | 메모리(Search) |
|------|----------|--------|----------------|----------------|
| 기본 구현 | 4.90s | 8.19s | 8.67 MB | 61.36 MB |
| 최적화 버전 | 0.94s | 1.16s | 8.67 MB | 61.36 MB |
| **개선율** | **5.2x** | **7.1x** | - | - |

[기본 구현]

<img width="667" height="417" alt="Image" src="https://github.com/user-attachments/assets/dfc7cd5d-70ec-4261-9614-c6920938a7b3" />

[최적화 버전]

<img width="668" height="417" alt="Image" src="https://github.com/user-attachments/assets/10593251-5d62-46c3-8ec3-ff138258e320" />

---

### 7.4 성능 개선 요약

| 연산 | 평균 개선율 | 주요 원인 |
|------|-------------|-----------|
| **Search** | **~10x** | `bisect_left` 이진 탐색 + 반복문 전환 |
| **Deletion** | **~6.5x** | `bisect_left` 이진 탐색 |
| **Insertion** | **~1.1x** | 삽입 위치 탐색은 여전히 선형 |
| **메모리** | **~4% ↓** | `__slots__` 적용 |

---

### 7.5 분석

#### Search 성능 (7x ~ 12x 개선)
- `bisect_left`로 node 내 탐색 복잡도 O(n) → O(log n)
- 재귀 → 반복문 전환으로 함수 호출 Overhead 제거
- t=100 기준, node당 최대 199개 key에서 비교 횟수: 199회 → 8회

#### Deletion 성능 (5x ~ 8x 개선)
- `_delete` 메서드 내 key 탐색에 `bisect_left` 적용
- 삭제 후 재균형 과정에서도 binary search 활용

#### Insertion 성능 (~1.1x 개선)
- `insert_notfull`의 삽입 위치 탐색은 여전히 linear search
- 리스트 `insert()` 연산 자체의 O(n) 비용 때문에 삽입 위치 탐색 최적화의 효과가 제한적

#### 메모리 사용량 (~4% 감소)
- `__slots__`로 instance당 dictionary overhead 제거
- 100만 개 records 기준, 약 0.8MB 절감

## 8. 코드에 대한 간단한 설명

### 8-1. Node Class

#### 속성 정의

```python
class Node:
    def __init__(self, leaf=True):
        self.keys = []   # 키 리스트 (정렬된 상태 유지)
        self.vals = []   # 값 리스트 (keys와 1:1 대응)
        self.kids = []   # 자식 노드 리스트
        self.leaf = leaf # 리프 노드 여부
```

| 속성 | 타입 | 설명 |
|------|------|------|
| `keys` | list[int] | 정렬된 키들 |
| `vals` | list[any] | 키에 대응하는 값들 |
| `kids` | list[Node] | 자식 노드들 (리프면 비어있음) |
| `leaf` | bool | True면 리프 노드 |

#### Node Structure

```
Internal Node:               Leaf Node:
┌─────────────────────┐      ┌─────────────────────┐
│ keys: [10, 20, 30]  │      │ keys: [10, 20, 30]  │
│ vals: [v1, v2, v3]  │      │ vals: [v1, v2, v3]  │
│ kids: [c0,c1,c2,c3] │      │ kids: []            │
│ leaf: False         │      │ leaf: True          │
└─────────────────────┘      └─────────────────────┘
      ↓   ↓   ↓   ↓
     c0  c1  c2  c3
```

#### keys와 kids의 관계

```
       keys:  [  10  ,  20  ,  30  ]
              ↑      ↑      ↑      ↑
       kids: [c0]  [c1]  [c2]  [c3]
              │      │      │      │
              ▼      ▼      ▼      ▼
            <10   10~20  20~30   >30
```

- `kids[i]`의 모든 키 < `keys[i]`
- `kids[i+1]`의 모든 키 > `keys[i]`
- **항상**: `len(kids) == len(keys) + 1` (내부 노드일 때)

### 8-2. BTree Class 초기화

```python
class BTree:
    def __init__(self, t=100):
        self.t = t           # minimum degree (최소 차수)
        self.root = Node()   # 빈 루트 노드로 시작
```

#### Minimum Degree (t) 의미

| t 기준 | 조건 |
|--------|------|
| 노드당 최소 키 (루트 제외) | t - 1 |
| 노드당 최대 키 | 2t - 1 |
| 노드당 최소 자식 (루트 제외) | t |
| 노드당 최대 자식 | 2t |

**t=100일 때**:
- 최소 키: 99개
- 최대 키: 199개
- 최소 자식: 100개
- 최대 자식: 200개

### 8-3. Search

```
검색 방식: Top-Down 재귀 탐색
시간 복잡도: O(t × log_t n)  [linear search 버전]
           O(log t × log_t n)  [binary search 버전]
```

![Image](https://github.com/user-attachments/assets/2a4d74fd-e54d-4d95-971b-07dc1efa65c5)

#### Step 1: 시작 노드 설정

```python
def search(self, k, n=None):
    # Step 1: 시작 노드 설정
    if n is None:
        n = self.root
```

**첫 호출 시 루트에서 시작**, 재귀 호출 시에는 자식 노드가 전달됨

#### Step 2: 현재 노드에서 키 위치 탐색 (Linear Search)

```python
    # Step 2: 현재 노드에서 키 위치 탐색 (Linear Search)
    i = 0
    while i < len(n.keys) and k > n.keys[i]:
        i += 1
```

[Linear Search 동작 원리]
```
예시: keys = [10, 30, 50, 70], k = 45

i=0: 45 > 10? Yes → i++
i=1: 45 > 30? Yes → i++
i=2: 45 > 50? No  → 종료

결과: i = 2
의미: k는 keys[1](=30)과 keys[2](=50) 사이에 있음
     → kids[2]에서 찾아야 함
```

#### Step 3: 키를 찾은 경우

```python
    # Step 3: 키를 찾은 경우
    if i < len(n.keys) and k == n.keys[i]:
        return n.vals[i]
```

**키 발견 시 즉시 값 반환**

```
keys = [10, 30, 50], k = 30

i=0: 30 > 10? Yes → i++
i=1: 30 > 30? No  → 종료
     i=1, keys[1] == 30 → 찾음!

return vals[1]
```

#### Step 4: 리프 노드인데 키가 없는 경우

```python
    # Step 4: 리프 노드인데 키가 없는 경우
    elif n.leaf:
        return None
```

**리프까지 내려왔는데 키가 없으면** → 트리에 존재하지 않음

```
Tree:       [30]
           /    \
        [10]    [50]
        
search(25):
- root [30]: 25 < 30 → kids[0]으로
- [10]: 25 > 10, leaf이고 키 없음 → return None
```

#### Step 5: 내부 노드면 자식으로 재귀

```python
    # Step 5: 내부 노드면 자식으로 재귀
    else:
        return self.search(k, n.kids[i])
```

**적절한 자식 노드로 내려가서 계속 탐색**

```
Tree:           [30, 60]
               /   |    \
           [10,20][40,50][70,80]
           
search(45):
- root [30,60]: i=1 (30 < 45 < 60)
  → kids[1] = [40,50]으로 재귀
- [40,50]: i=1 (40 < 45 < 50)
  → leaf이고 키 없음 → return None
```

### 8-4. Insertion

```
삽입 방식: Proactive Top-Down Split
핵심 원리: "삽입은 항상 리프에서, 하지만 내려가면서 미리 split"
시간 복잡도: O(t × log_t n)
```

**Proactive Split**: 내려가기 **전에** 가득 찬 노드를 미리 split  
**Reactive Split**: 삽입 **후에** 넘치면 올라오며 split

→ Proactive Split이 더 효율적 (재귀 호출 횟수 감소)
→ 해당 코드에서는 Proactive Split Top-Down 방식으로 구현

```
Proactive Split (현재 구현):
    [Full]              [Split]
       ↓          →        ↓
    [Node]              [Node]
       ↓                   ↓
    [Leaf] ← 삽입      [Leaf] ← 안전하게 삽입
    
Reactive Split:
    [Node]              [Node] ← split 전파
       ↓                   ↑
    [Leaf] ← 삽입      [Overflow!]
```

![Image](https://github.com/user-attachments/assets/e43ac0c2-35b9-46d3-8621-4263b0284401)

![Image](https://github.com/user-attachments/assets/91787c97-340f-4316-95fc-7ebbcb4ee5c6)

### 8-5. Deletion

**"내려가면서 미리 준비하는"** Top-Down 방식

```
        [Root]
           ↓  ← 내려가기 전에 미리 fill() 호출
        [Node]
           ↓  ← 키 개수가 충분한 상태로 내려감
        [Leaf] ← 여기서 삭제해도 underflow 걱정 없음
```

### Top-Down vs Bottom-Up 비교

| 특성 | Top-Down (Proactive) | Bottom-Up (Reactive) |
|------|----------------------|----------------------|
| **동작 시점** | 자식으로 내려가기 **전에** 조정 | 삭제 **후에** 올라오며 조정 |
| **조정 방향** | 루트 → 리프 (하향) | 리프 → 루트 (상향) |
| **장점** | 한 번의 하향 순회로 완료 | 구현이 직관적 |
| **단점** | 불필요한 조정 가능성 | 부모 포인터 필요 또는 재귀 스택 |
| **현재 코드** | ✅ 이 방식 | - |

```python
def _delete(self, n, k):
    ...
    else:
        # 3) key가 현재 node에 존재하지 않을 때
        if n.leaf:
            return
        
        # ★★★ 핵심: 자식으로 내려가기 "전에" fill() 호출 ★★★
        if len(n.kids[i].keys) < t:
            self.fill(n, i)  # ← 미리 키 개수 확보!
        
        # fill 후에 안전하게 내려감
        self._delete(n.kids[i], k)  # ← 이제 내려가도 안전
```

| 특징 | 설명 |
|------|------|
| **방식** | Top-Down (Proactive) |
| **장점** | 한 번의 하향 순회로 삭제 완료 |
| **키 탐색** | Linear search (`while i < len(n.keys)`) |
| **내부 노드 삭제** | Predecessor 우선, Successor 차선, Merge 최후 |
| **Underflow 방지** | 자식 진입 전 `fill()` 호출 |
| **fill() 우선순위** | Borrow Left → Borrow Right → Merge |
| **트리 높이 감소** | 루트가 비면 자식을 새 루트로 승격 |

![Image](https://github.com/user-attachments/assets/e4a74761-858f-4c96-a435-221991e19b45)

![Image](https://github.com/user-attachments/assets/3313c35e-ad75-47ba-8660-8690f73b7ae7)