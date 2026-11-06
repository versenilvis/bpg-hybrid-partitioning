from __future__ import annotations
try:
    from . import config
    from .partition_scheme import PartitionScheme, CreatePartitionScheme
    from .partitioning import FirstPartitioning, Partitioning, PartitioningUnbalancedGraph, PartitioningMinimumCutGraph
    from .bpg import PartitionScheme_BPG, BregmanProximalGradient, BPG_PartitionScheme, bpg_partition
except ImportError:
    import config
    from partition_scheme import PartitionScheme, CreatePartitionScheme
    from partitioning import FirstPartitioning, Partitioning, PartitioningUnbalancedGraph, PartitioningMinimumCutGraph
    from bpg import PartitionScheme_BPG, BregmanProximalGradient, BPG_PartitionScheme, bpg_partition

__all__ = [
    'config',
    'PartitionScheme',
    'CreatePartitionScheme',
    'FirstPartitioning',
    'Partitioning',
    'PartitioningUnbalancedGraph',
    'PartitioningMinimumCutGraph',
    'PartitionScheme_BPG',
    'BPG_PartitionScheme',
    'BregmanProximalGradient',
    'bpg_partition',
]

