# BPG-Based Initial Partitioning for Hybrid Data Partitioning in NewSQL Databases

Tạm dịch: Thay thế thuật toán khởi tạo bằng BPG cho phương pháp phân mảnh dữ liệu hybrid trong hệ cơ sở dữ liệu NewSQL

Dự án hiện thực hóa thuật toán Bregman Proximal Gradient (BPG) cho bài toán phân bổ dữ liệu khởi tạo trong các phương án phân mảnh hybrid cho hệ cơ sở dữ liệu phân tán NewSQL

Mã nguồn này thay thế thuật toán phân mảnh khởi đầu tham lam (Algorithm 5 của Schreiner và cộng sự) bằng mô hình tối ưu Normalized Cut liên tục được giải bằng BPG (Niu và cộng sự) nhằm giảm thiểu chi phí nghẽn mạng do giao dịch phân tán và cân bằng tải công việc giữa các máy chủ

---

## Cài đặt

```bash
pip install bpg-partitioning
```

Chạy nhanh kịch bản mô phỏng đối chiếu trên terminal:

```bash
bpg-partitioning
```

---

## Ví dụ sử dụng nhanh

```python
import bpg_partitioning as bp

# tạo dữ liệu giả lập và đồ thị nhiệt
creator = bp.CreatePartitionScheme(num_records=5, seed=42)
scheme = creator.run()

# phân mảnh khởi tạo bằng bpg
bpg_scheme = bp.bpg_partition(scheme, site_num=2, step_size=1.0, iterations_num=50, seed=42)
print(bpg_scheme.partitions)

# chạy điều phối phân mảnh thích ứng động (algorithm 2) kết hợp bpg
dyn_scheme = bp.Partitioning(
    partition_scheme=creator.run(),
    site_num=2,
    workload_factor=0.2,
    distributed_percentage=0.02,
    use_bpg=True
).run()
print(dyn_scheme.partitions)
```

---

## Tài liệu API và kiểu trả về

### 1. Cấu trúc dữ liệu và khởi tạo đồ thị nhiệt

#### `PartitionScheme(heat_graph: nx.Graph, partitions: dict[int, set[int]])`
Cấu trúc dữ liệu trung tâm lưu trữ trạng thái phân mảnh của hệ thống:
* `heat_graph` (`nx.Graph`): Đồ thị nhiệt với mỗi đỉnh là một projection thuộc tính (`tuple_id: int`, `table: str`, `attrs: list[str]`, `weight: float`) và mỗi cạnh mang trọng số `weight: float` (`0.0` cho các mảnh cùng một tuple, `> 0.0` cho tần suất đồng truy cập trong giao dịch)
* `partitions` (`dict[int, set[int]]`): Từ điển ánh xạ từ mã máy chủ (`site_id`) sang tập hợp các mã đỉnh (`set[int]`) được đặt tại máy chủ đó

#### `CreatePartitionScheme(num_records: int = 5, seed: int = 42)`
Bộ sinh dữ liệu khách hàng, giao dịch giả lập và đồ thị nhiệt:
* `generate_mock_data() -> list[dict]`: Trả về danh sách các bản ghi khách hàng gồm `id`, `name`, `email`, `phone`, `city`, `balance`
* `generate_mock_transactions(num_transactions: int = 10) -> list[dict]`: Trả về danh sách giao dịch dạng `{'tx_id': int, 'ops': list[{'tuple_id': int, 'attrs': list[str]}]}`
* `build_heat_graph() -> nx.Graph`: Xây dựng và trả về đối tượng đồ thị nhiệt `nx.Graph` từ danh sách giao dịch
* `run() -> PartitionScheme`: Thực thi toàn bộ quy trình sinh dữ liệu và trả về `PartitionScheme` ban đầu với mọi đỉnh nằm chung tại phân vùng `0` (`{0: set(nodes)}`)

---

### 2. Nhóm thuật toán Bregman Proximal Gradient (BPG)

#### `bpg_partition(partition_scheme: PartitionScheme, site_num: int = 2, step_size: float = 1.0, iterations_num: int = 50, seed: int = 42) -> PartitionScheme`
Hàm gọi nhanh toàn bộ chu trình phân mảnh bằng BPG (gom cụm cạnh 0 -> giải tối ưu Normalized Cut -> ánh xạ về phân vùng):
* **Return**: `PartitionScheme` mới với `partitions` chứa các khóa phân vùng từ `1` đến `site_num`

#### `PartitionScheme_BPG(partition_scheme: PartitionScheme, use_coarsening: bool = True)`
Chuyển đổi đồ thị nhiệt sang ma trận ái lực thưa:
* `run() -> scipy.sparse.csr_array`: Gom các đỉnh nối bởi cạnh trọng số `0.0` (khi `use_coarsening=True`) và trả về ma trận kề đối xứng `W` kích thước `(N, N)` dạng `csr_array`
* **Thuộc tính sau khi chạy**:
  * `W` (`csr_array`): Ma trận ái lực giữa các tuple
  * `coarse_to_nodes` (`dict[int, list[int]]`): Ánh xạ từ chỉ số cụm thu gọn sang danh sách các `node_id` gốc trên đồ thị nhiệt
  * `node_to_idx`, `idx_to_node` (`dict[int, int]`): Ánh xạ hai chiều giữa ID đỉnh thu gọn và chỉ số hàng/cột của ma trận

#### `BregmanProximalGradient(W: csr_array, partitions_num: int, step_size: float, iterations_num: int, seed: int | None = None)`
Bộ giải tối ưu liên tục Normalized Cut bằng cập nhật hàm mũ và phép chiếu Bregman:
* `run() -> np.ndarray`: Trả về mảng 1 chiều `labels` (`np.ndarray` kiểu số nguyên kích thước `(N,)`, giá trị nhãn nằm trong đoạn `[1, partitions_num]`)
* **Thuộc tính sau khi chạy**:
  * `X` (`np.ndarray`): Ma trận phân bổ xác suất mềm kích thước `(N, partitions_num)` trước khi rời rạc hóa bằng `argmax`

#### `BPG_PartitionScheme(heat_graph: nx.Graph, labels: np.ndarray, coarse_to_nodes: dict[int, list[int]] | None = None)`
Chuyển đổi nhãn phân cụm từ bộ giải BPG về lại cấu trúc phân mảnh:
* `run() -> PartitionScheme`: Bung các nhãn cụm về lại các đỉnh projection gốc trên `heat_graph` và trả về `PartitionScheme`

---

### 3. Nhóm thuật toán phân mảnh thích ứng (Autonomous NewSQL)

#### `FirstPartitioning(partition_scheme: PartitionScheme, site_num: int)` (Algorithm 5)
Thuật toán phân mảnh khởi tạo tham lam dùng làm cơ sở đối chiếu (baseline):
* `run() -> PartitionScheme`: Gom cụm cạnh 0, chọn `site_num` đỉnh có trọng số nhiệt lớn nhất làm hạt giống (seed) cho từng site rồi phân bổ phần còn lại theo độ liên kết và cân bằng tải; cập nhật tại chỗ và trả về `PartitionScheme` với khóa site từ `0` đến `site_num - 1` (quăng `ValueError` nếu `site_num <= 0` hoặc không nguyên)

#### `Partitioning(partition_scheme: PartitionScheme, site_num: int, workload_factor: float, distributed_percentage: float = 0.02, use_bpg: bool = False)` (Algorithm 2)
Bộ điều phối phân mảnh thích ứng động:
* `getLoads(partition_scheme: PartitionScheme) -> list[float]`: Trả về danh sách tổng trọng số nhiệt của từng phân vùng
* `getCriticalEdgesLoad(partition_scheme: PartitionScheme) -> float`: Trả về tổng trọng số của tất cả các cạnh bị cắt qua nhiều phân vùng
* `run(recursion_depth: int = 20) -> PartitionScheme`: Tự động kiểm tra độ lệch tải (gọi `PartitioningUnbalancedGraph`), kiểm tra tỷ lệ giao dịch phân tán (gọi `PartitioningMinimumCutGraph`), và khởi tạo phân mảnh (bằng `bpg_partition` nếu `use_bpg=True`, ngược lại dùng `FirstPartitioning`) khi hệ thống mới chỉ có 1 phân vùng; trả về `PartitionScheme` đã tối ưu

#### `PartitioningUnbalancedGraph(partition_scheme: PartitionScheme, site_num: int, workload_factor: float)` (Algorithm 3)
Thuật toán tái cân bằng khi có máy chủ vượt ngưỡng tải `(1 ± workload_factor) * avg_load`:
* `getLoads(partition_scheme: PartitionScheme) -> dict[int, float]`: Trả về từ điển `{partition_id: total_weight}`
* `mostProeminentTuple(partition_scheme: PartitionScheme, overloadedPartition: int) -> int | None`: Trả về `node_id` có trọng số nhiệt lớn nhất và tổng trọng số cạnh kề nhỏ nhất trong phân vùng quá tải (hoặc `None` nếu phân vùng rỗng)
* `relocateTuple(partition_scheme: PartitionScheme, proeminent_tuple: int, underloadPartition: int, overloadPartition: int) -> bool`: Chuyển đỉnh sang phân vùng nhẹ tải nếu không làm phân vùng đích vượt ngưỡng tải tối đa, trả về `True` nếu chuyển thành công và `False` nếu từ chối
* `run(recursion_depth: int = 20) -> PartitionScheme`: Trả về bản sao `PartitionScheme` sau khi đã cân bằng tải

#### `PartitioningMinimumCutGraph(partition_scheme: PartitionScheme, workload_factor: float, depth_search: int = 2)` (Algorithm 4)
Thuật toán giảm chi phí giao dịch phân tán bằng di chuyển cụm đỉnh lân cận hoặc nhân bản dữ liệu:
* `criticalEdges(partition_scheme: PartitionScheme) -> list[tuple[int, int, float]]`: Trả về danh sách `(u, v, weight)` của các cạnh có `weight > 0` mà hai đầu mút không có phân vùng chung
* `hottestEdge(criticalEdges: list[tuple[int, int, float]]) -> tuple[int, int, float]`: Trả về cạnh `(u, v, weight)` có trọng số lớn nhất
* `calculateMinimumCut(partition_scheme: PartitionScheme) -> float`: Trả về tổng trọng số các cạnh cắt
* `checkBalance(partition_scheme: PartitionScheme) -> bool`: Kiểm tra mọi phân vùng có thỏa mãn giới hạn tải Equation 1 hay không
* `checkMinPartition(original_scheme: PartitionScheme, new_scheme: PartitionScheme) -> bool`: Kiểm tra phương án mới có tổng trọng số cắt nhỏ hơn hẳn phương án cũ hay không (Equation 2)
* `updateMinCut(partition_scheme: PartitionScheme, vertex_groups, origin_partition: int, target_partition: int) -> tuple[float, list[int]]`: Thử nghiệm các nhóm đỉnh ứng viên và trả về `(minimal_cut, best_vertices)` thỏa mãn cân bằng tải có vết cắt nhỏ nhất
* `explorePossibility(partition_scheme: PartitionScheme, vertex: int, origin_partition: int, target_partition: int) -> tuple[float, list[int]]`: Dò tìm phương án di chuyển từ 0-hop đến `depth_search` hops, trả về `(minimal_cut, best_vertices)` nếu giảm được vết cắt hiện tại, ngược lại trả về `(-1, [])`
* `createReplication(partition_scheme: PartitionScheme, vertex: int, target_partition: int) -> PartitionScheme`: Nhân bản đỉnh `vertex` sang `target_partition` (giữ nguyên đỉnh gốc)
* `explorePossibilititesReplication(partition_scheme: PartitionScheme, vertex_one: int, vertex_two: int, partition_one: int, partition_two: int) -> PartitionScheme`: Thử nhân bản một trong hai đầu mút của cạnh cắt nếu thỏa mãn đồng thời Equation 1 và Equation 2, trả về `PartitionScheme` mới
* `run() -> PartitionScheme`: Duyệt các cạnh cắt theo trọng số giảm dần để di chuyển hoặc tạo bản sao tối ưu, trả về bản sao `PartitionScheme` đã giảm vết cắt

---

## Tài liệu tham khảo

[1] P. Niu, B. Ren, H. Wu, and X. Yao, "Modeling and optimization for massive data allocation in database," arXiv:2605.31002, Jun 2026

[2] G. A. Schreiner, R. de Santiago, D. Duarte, and R. dos Santos Mello, "An autonomous hybrid data partitioning approach for NewSQL databases," Journal of the Brazilian Computer Society, vol. 32, no. 1, Art. no. 1, 2026, doi: 10.5753/jbcs.2026.5684
