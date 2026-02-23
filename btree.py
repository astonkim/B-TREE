import time
import tracemalloc

class Node:
    def __init__(self, leaf=True):
        self.keys = []
        self.vals = []
        self.kids = []
        self.leaf = leaf

class BTree:
    def __init__(self, t=100):
        # 최소 차수
        self.t = t
        # 빈 트리로 초기화
        self.root = Node()

    # Search 메서드
    # k: 검색할 key, n: 현재 node (default: 루트 node), i: 현재 key의 인덱스
    def search(self, k, n=None):
        if n is None:
            n = self.root
        # 현재 node의 키들을 순회하며 검색 (linear search)
        # key가 현재 node의 key보다 클 때까지 인덱스 증가
        i = 0
        while i < len(n.keys) and k > n.keys[i]:
            i += 1
        # key를 찾았을 때: key가 현재 node의 key와 같으면 해당 value 반환
        if i < len(n.keys) and k == n.keys[i]:
            return n.vals[i]
        # 현재 node가 리프 노드이면 None 반환
        elif n.leaf:
            return None
        else:
            return self.search(k, n.kids[i])
    
    # Insert 메서드
    # rn: 현재 root node, k: 삽입할 key, v: 삽입할 value
    def insert(self, k, v):
        rn = self.root
        # root node가 가득 찼을 때: 새로운 root node를 만들고 기존 root를 child로 추가
        # 그리고 split 후에 삽입
        if len(rn.keys) == 2*self.t - 1:
            s = Node(leaf=False)
            self.root = s
            s.kids.append(rn)
            self.split(s, 0)
            self.insert_nonfull(s, k, v)
        # root node가 가득 차지 않았을 때: 바로 삽입
        else:
            self.insert_nonfull(rn, k, v)

    # node split 메서드
    # t: 최소 차수, pn: 분할할 parent node, cn_index: 분할할 child node의 인덱스, cn: 분할할 child node, new_n: 새로 생성할 node
    def split(self, pn, cn_index):
        t = self.t
        cn = pn.kids[cn_index]
        new_n = Node(leaf=cn.leaf)
        # 중간 인덱스
        mid = t - 1
        
        # new_n은 상위 절반을 가짐
        new_n.keys = cn.keys[t:]
        new_n.vals = cn.vals[t:]
        if not cn.leaf:
            new_n.kids = cn.kids[t:]
        
        # 중간값을 부모로 승격
        pn.keys.insert(cn_index, cn.keys[mid])
        pn.vals.insert(cn_index, cn.vals[mid])
        pn.kids.insert(cn_index + 1, new_n)
        
        # cn은 하위 절반을 가짐
        cn.keys = cn.keys[:mid]
        cn.vals = cn.vals[:mid]
        if not cn.leaf:
            cn.kids = cn.kids[:t]

    # 재귀적으로 삽입하는 메서드 (node가 가득 차지 않은 node에 삽입) - n: 현재 node, k: 삽입할 key, v: 삽입할 value
    def insert_nonfull(self, n, k, v):
            i = len(n.keys) - 1
            # leaf node일 때: 적절한 위치를 찾아 key와 value 삽입
            if n.leaf:
                while i >= 0 and k < n.keys[i]:
                    i -= 1
                n.keys.insert(i + 1, k)
                n.vals.insert(i + 1, v)
            else:
                # 리프 노드가 아닐 때: 적절한 자식 노드를 찾아 재귀적으로 삽입
                while i >= 0 and k < n.keys[i]:
                    i -= 1
                i += 1
                if len(n.kids[i].keys) == 2*self.t - 1:
                    self.split(n, i)
                    if k > n.keys[i]:
                        i += 1
                self.insert_nonfull(n.kids[i], k, v)
    
    # Delete 메서드 - k: 삭제할 key
    def delete(self, k):
        self._delete(self.root, k)
        # root node가 비어있으면 child node를 새로운 root로 설정
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.kids[0]
    
    # n: 현재 node, k: 삭제할 key
    def _delete(self, n, k):
        t = self.t
        # 현재 node에서 key의 위치를 찾음
        i = 0
        while i < len(n.keys) and k > n.keys[i]:
            i += 1
        
        # 1) key가 현재 node에 존재할 때
        if i < len(n.keys) and n.keys[i] == k:
            if n.leaf:
                # 1-1) leaf node일 때: key와 value 단순 삭제
                n.keys.pop(i)
                n.vals.pop(i)
            else:
                # 2) internal node일 때: 세 가지 경우로 나눔 (아래에서 구현 예정)
                self.delete_internal_node(n, i)
        else:
            # 3) key가 현재 node에 존재하지 않을 때: child node로 내려가서 삭제
            if n.leaf:
                return  # key가 트리에 존재하지 않음
            
            # child node가 최소 키 수보다 적을 때: child node를 채우기 (key 개수 확보)
            if len(n.kids[i].keys) < t:
                self.fill(n, i)
                
            #fill 후에 child node가 변경될 수 있으므로 다시 탐색 (index i 조정)
            if i > len(n.keys):
                i -= 1
            
            self._delete(n.kids[i], k)
    
    # internal node에서 key 삭제 처리 메서드 - n: 현재 node, i: 삭제할 key의 인덱스
    def delete_internal_node(self, n, i):
        t = self.t
        k = n.keys[i]
    
    # 2-1) 삭제할 key의 왼쪽 child node가 t개 이상의 key를 가지고 있을 때: 왼쪽 child node에서 가장 큰 key를 찾아 삭제할 key와 교체 후 재귀적으로 삭제
        if len(n.kids[i].keys) >= t:
            predecessor_k, predecessor_v = self.get_predecessor(n, i) # get_predecessor 아래에서 구현 예정
            n.keys[i] = predecessor_k
            n.vals[i] = predecessor_v
            self._delete(n.kids[i], predecessor_k)
    # 2-2) 삭제할 key의 오른쪽 child node가 t개 이상의 key를 가지고 있을 때: 오른쪽 child node에서 가장 작은 key를 찾아 삭제할 key와 교체 후 재귀적으로 삭제
        elif len(n.kids[i+1].keys) >= t:
            successor_k, successor_v = self.get_successor(n, i) # get_successor 아래에서 구현 예정
            n.keys[i] = successor_k
            n.vals[i] = successor_v
            self._delete(n.kids[i+1], successor_k)
            
    # 2-3) 삭제할 key의 양쪽 child node가 모두 t-1개 이하의 key를 가지고 있을 때: 왼쪽과 오른쪽 child node를 병합한 후 삭제할 key가 포함된 새로운 child node에서 재귀적으로 삭제
        else:
            self.merge(n, i) # merge 아래에서 구현 예정
            self._delete(n.kids[i], k)
    
    # predecessor와 successor를 찾는 메서드 - n: 현재 node, i: key의 인덱스
    def get_predecessor(self, n, i):
        # 왼쪽 subtree에서 가장 큰 key를 찾음
        current = n.kids[i]
        while not current.leaf:
            current = current.kids[-1]
        return current.keys[-1], current.vals[-1]
    def get_successor(self, n, i):
        # 오른쪽 subtree에서 가장 작은 key를 찾음
        current = n.kids[i+1]
        while not current.leaf:
            current = current.kids[0]
        return current.keys[0], current.vals[0]
    
    # child node를 채우는 메서드 - n: 현재 node, i: 채울 child node의 인덱스
    def fill(self, n, i):
        t = self.t
        
        # 1) 왼쪽 sibling이 t개 이상의 key를 가지고 있을 때: 왼쪽 sibling에서 key를 빌려옴
        if i > 0 and len(n.kids[i-1].keys) >= t:
            self.borrow_left(n, i) # borrow_left 아래에서 구현 예정
        # 2) 오른쪽 sibling이 t개 이상의 key를 가지고 있을 때: 오른쪽 sibling에서 key를 빌려옴
        elif i < len(n.kids) - 1 and len(n.kids[i+1].keys) >= t:
            self.borrow_right(n, i) # borrow_right 아래에서 구현 예정
        # 3) 양쪽 sibling이 모두 t-1개 이하의 key를 가지고 있을 때: sibling과 병합
        else:
            if i < len(n.kids) - 1:
                self.merge(n, i) # merge 아래에서 구현 예정
            else:
                self.merge(n, i-1) # merge 아래에서 구현 예정
    
    # 왼쪽 sibling에서 key를 빌려오는 메서드 - n: 현재 node, i: child node의 인덱스
    def borrow_left(self, n, i):
        child = n.kids[i]
        sibling = n.kids[i-1]
        
        # parent key를 child 앞에 삽입
        child.keys.insert(0, n.keys[i-1])
        child.vals.insert(0, n.vals[i-1])
        
        # sibling의 마지막 key를 parent로 이동
        n.keys[i-1] = sibling.keys.pop()
        n.vals[i-1] = sibling.vals.pop()
        
        # sibling의 마지막 child를 child의 첫 번째 child로 이동 (leaf가 아닐 때)
        if not sibling.leaf:
            child.kids.insert(0, sibling.kids.pop())
    
    # 오른쪽 sibling에서 key를 빌려오는 메서드 - n: 현재 node, i: child node의 인덱스
    def borrow_right(self, n, i):
        child = n.kids[i]
        sibling = n.kids[i+1]
        
        # parent key를 child 뒤에 삽입
        child.keys.append(n.keys[i])
        child.vals.append(n.vals[i])
        
        # sibling의 첫 번째 key를 parent로 이동
        n.keys[i] = sibling.keys.pop(0)
        n.vals[i] = sibling.vals.pop(0)
        
        # sibling의 첫 번째 child를 child의 마지막 child로 이동 (leaf가 아닐 때)
        if not sibling.leaf:
            child.kids.append(sibling.kids.pop(0))
    
    # 두 child node를 병합하는 메서드 - n: 현재 node, i: 병합할 child node의 인덱스
    def merge(self, n, i):
        left = n.kids[i]
        right = n.kids[i+1]
        
        # parent key를 left child에 추가
        left.keys.append(n.keys.pop(i))
        left.vals.append(n.vals.pop(i))
        
        # right child의 key와 value를 left child에 병합
        left.keys.extend(right.keys)
        left.vals.extend(right.vals)
        if not left.leaf:
            left.kids.extend(right.kids)
        
        # parent에서 right child 제거
        n.kids.pop(i+1)
        
        
# 메모리 사용량 포맷 함수
def format_memory(bytes):
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024*1024:
        return f"{bytes / 1024:.2f} KB"
    else:
        return f"{bytes / 1024 / 1024:.2f} MB"
    
# 데이터 파일에서 key-value 쌍 load
def load_data(filename):
    data = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            p = line.split('\t')
            if len(p) >= 2:
                data.append((int(p[0]), int(p[1])))
    return data

# 삽입 작업 수행
def run_insert(tree, path):
    print(f"\nLoading {path}...")
    data = load_data(path)
    print(f"Loaded {len(data)} records.")
    
    tracemalloc.start()
    print("Inserting...", end='', flush=True)
    t0 = time.time()
    for k, v in data:
        tree.insert(k, v)
    t1 = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f" Done in {t1 - t0:.2f} seconds.")
    print(f" Memory usage: Current: {format_memory(current)}, Peak: {format_memory(peak)}")
    
    return data

# 검색 작업 수행
def run_search(tree, data, outpath):
    tracemalloc.start()
    print("Searching...", end='', flush=True)
    t0 = time.time()
    
    results = []
    for k, _ in data:
        v = tree.search(k)
        results.append((k, v))
    
    t1 = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f" Done in {t1 - t0:.2f} seconds.")
    print(f" Memory usage: Current: {format_memory(current)}, Peak: {format_memory(peak)}")
    
    print(f"Writing results to {outpath}...", end='', flush=True)
    with open(outpath, 'w') as f:
        for k, v in results:
            if v is not None:
                f.write(f"{k}\t{v}\n")
            else:
                f.write(f"{k}\tN/A\n")
    print(" Done.")
    
    return results

# 삭제 작업 수행
def run_delete(tree, data, path):
    print(f"\nLoading {path} for deletion...")
    data = load_data(path)
    print(f"Loaded {len(data)} records for deletion.")
    
    tracemalloc.start()
    print("Deleting...", end='', flush=True)
    t0 = time.time()
    
    for k, _ in data:
        tree.delete(k)
    
    t1 = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f" Done in {t1 - t0:.2f} seconds.")
    print(f" Memory usage: Current: {format_memory(current)}, Peak: {format_memory(peak)}")
    
    return data

# 파일 비교 함수
def compare_files(f1, f2):
    print(f"Comparing {f1} vs {f2}...", end='', flush=True)
    
    with open(f1, 'r') as file1, open(f2, 'r') as file2:
        lines1 = file1.readlines()
        lines2 = file2.readlines()
    
    if len(lines1) != len(lines2):
        print(f"MISMATCH (line count differs: {len(lines1)} vs {len(lines2)})")
        return False
    
    diff = 0
    for i, (l1, l2) in enumerate(zip(lines1, lines2)):
        if l1.strip() != l2.strip():
            diff += 1
            if diff <= 3:
                print(f"\n  Line {i+1}: '{l1.strip()}' vs '{l2.strip()}'")

    if diff == 0:
        print("MATCH")
        return True
    else:
        print(f"MISMATCH ({diff} differences)")
        return False

# 메뉴 출력 함수
def menu():
    print("\n" + "="*40)
    print("B-Tree Algorithm Test Menu - Kim Nammin")
    print("="*40)
    print("1. Insertion")
    print("2. Deletion")
    print("3. Quit")
    print("="*40)
    return input("Select an option (1-3): ").strip()

def main():
    tree = None
    data = None
    
    while True:
        choice = menu()
        
        if choice == "1":
            fname = input("Enter input file name(e.g., input.csv, input22.csv): ").strip()
            try:
                # 새로운 B-Tree 인스턴스 생성 (매 삽입마다 초기화)
                tree = BTree(t=100)
                data = run_insert(tree, fname)
                run_search(tree, data, "search_result.csv")
                compare_files(fname, "search_result.csv")
            except FileNotFoundError:
                print(f"File '{fname}' not found. Please try again.")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == "2":
            if tree is None or data is None:
                print("Error: Insert data first")
                continue 
            del_fname = input("Enter delete file name(e.g., delete.csv, delete2.csv): ").strip()
            cmp_fname = input("Enter compare file name(e.g., delete_compare.csv, delete_compare2.csv): ").strip()
            try:
                run_delete(tree, data, del_fname)
                run_search(tree, data, "delete_result.csv")
                compare_files("delete_result.csv", cmp_fname)
            except FileNotFoundError:
                print(f"Error: file not found - {e}")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == "3":
            print("Exiting program. Goodbye!")
            print("Copyright (c) 2026 Kim Nammin. All rights reserved.")
            print ("="*40)
            break
        
        else:
            print("Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()