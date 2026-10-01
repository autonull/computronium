"""Peer-to-peer distributed training (Kademlia DHT + gRPC)."""

from computronium.p2p.dht import DHTNode
from computronium.p2p.grpc_service import (
    GRPCClient,
    GRPCConnectionPool,
    GRPCServer,
    TileMeshServicer,
)
from computronium.p2p.state import load_state, save_state

__all__ = [
    "DHTNode",
    "GRPCClient",
    "GRPCConnectionPool",
    "GRPCServer",
    "TileMeshServicer",
    "load_state",
    "save_state",
]
