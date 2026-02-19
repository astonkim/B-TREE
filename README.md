# B-TREE 구현

## 1. Functions

### Insertion & Searching
- input.csv에 있는 값들을 모두 읽어 삽입 연산 수행
- input.csv에 있는 100만개의 key들을 모두 search하여 그 value를 새로운 파일에 입력 한 뒤, 새 파일을 원래의 input.csv파일과 비교

### Deletion
- input.csv에 있는 100만개 key-value 쌍들 중 절반에 대하여 삭제 연산 수행
    - 삭제 대상인 key-value 쌍은 delete.csv에 제시되어 있음
- input.csv에 있는 100만개의 key들을 모두 search하여 그 value를 새로운 파일에 입력한 뒤, 새 파일을 delete_compare.csv 파일과 비교
    - 기존의 데이터셋에서 삭제된 value들은 생성된 새 파일 내에 “없는 값”(e.g. N/A, NF)이라고 출력되어야 함

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

```python
B-TREE/
├── btree.py          # 전부 여기에
├── input.csv         # 원본 (100만)
├── input22.csv         # 원본 (100만)
├── delete.csv        # 삭제 대상
├── search_result.csv # 검색 결과 출력용
└── delete_compare.csv # 삭제 후 비교용
```

## 5. 구현 순서
1) B-Tree Node 클래스 구현
    - keys, values, children, is_leaf 플래그 등의 속성 정의
2) B-Tree 클래스 구현
    - 삽입 연산 (insert)
    - 검색 연산 (search)
    - 삭제 연산 (delete)
3) 파일 I/O 함수 구현
4) 성능 평가 및 비교 함수 구현
5) main() - 메인 함수 구현 및 사용자 인터페이스 작성 (메뉴 루프)

## 6. B-Tree 정리

### 기본 속성 (m차 B-Tree invariants)
|속성|규칙|
|---|---|
|키 개수 (루트)|1 ≤ keys ≤ m-1|
|키 개수 (내부/리프)|⌈m/2⌉-1 ≤ keys ≤ m-1|
|자식 개수 (내부 노드)|⌈m/2⌉ ≤ children ≤ m|
|정렬|각 노드 내 키는 오름차순|
|균형|모든 리프 노드는 같은 깊이|

### Search
**Search(node, key):**
1. 현재 노드에서 key를 찾음
2. node가 none이면 "not found" 반환
3. node의 key list에서 key 위치 i 찾음
4. key가 node.keys[i]와 같으면 해당 value 반환
5. key가 node.keys[i]보다 작은 첫 번째 i 찾아 자식 node.children[i]로 재귀 탐색
6. key가 모든 keys보다 크면 마지막 자식 node.children[len(keys)]로 재귀 탐색

### Insertion
**"삽입은 항상 leaf node에서 시작, Overflow 시 부모 node로 split"**

**Insert(tree, key, value):**
1. 루트 node가 full인지 확인
2. tree가 비어있으면 새 루트 node 생성, key 삽입
3. 적절한 leaf node 찾기 위해 재귀적으로 이동 (각 단계에서 key와 현재 node의 keys 비교)
4. leaf node에 key-value 쌍 삽입 (오름차순 정렬 유지)
5. node의 key 개수가 m-1 초과 시 split 수행

**"node가 Overflow되면 (key 개수 > m-1)"**
**Split(node):**
1. 중간 키(median key, index = ⌊m/2⌋)를 찾음
2. node를 두 개의 node로 분할 (왼쪽 node(median 이전 keys)와 오른쪽 node(median 이후 keys))
3. median key를 부모 node로 올림 (승격)
4. 부모 node가 full이면(Overflow) 재귀적으로 split 수행
5. root가 split되면 새 root node 생성, tree 높이 증가

### Deletion

**Deletion(node, key):**
1. key 탐색
2. key가 leaf node에 있으면
    - key 삭제
    - underflow(키 개수 < ⌈m/2⌉-1) 발생 시 형제 노드에서 키 빌리기(Borrow) 또는 병합(Merge) 수행
3. key가 내부 노드에 있으면
    - key의 predecessor(왼쪽 서브트리에서 가장 큰 키) 또는 successor(오른쪽 서브트리에서 가장 작은 키)로 대체
    - 해당 key를 leaf node에서 재귀적으로 삭제
4. 재균형이 루트까지 전파될 수 있음
    - 루트가 비어있으면 자식이 새 루트가 됨, 트리 높이 감소