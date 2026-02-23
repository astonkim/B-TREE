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
