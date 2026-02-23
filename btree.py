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
            fname = input("Enter input file name for deletion(e.g., delete.csv, delete2.csv): ").strip()
            print("Deletion not implemented yet. Please try again later.")
        
        elif choice == "3":
            print("Exiting program. Goodbye!")
            print("Copyright (c) 2026 Kim Nammin. All rights reserved.")
            print ("="*40)
            break
        
        else:
            print("Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()