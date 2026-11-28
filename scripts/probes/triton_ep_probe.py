"""Chunked ep_settle vs torch: error growth over steps."""

import torch

from computronium.acceleration.triton_kernels import MEP_TritonOps

torch.manual_seed(42)
M, K, H = 8, 128, 512
for steps in (1, 2, 5, 30):
    h = torch.randn(M, K, device="cuda")
    xe = torch.randn(M, K, device="cuda")
    W1 = torch.randn(H, K, device="cuda")
    b1 = torch.randn(H, device="cuda")
    W2 = torch.randn(K, H, device="cuda")
    b2 = torch.randn(K, device="cuda")
    gamma = 0.5
    out = MEP_TritonOps.ep_settle(h, xe, W1, b1, W2, b2, gamma=gamma, steps=steps)
    r = h.clone()
    for _ in range(steps):
        mean = r.mean(-1, keepdim=True)
        std = r.std(-1, keepdim=True, correction=0) + 1e-5
        rn = (r - mean) / std
        r = (1 - gamma) * r + gamma * (torch.tanh(rn @ W1.T + b1) @ W2.T + b2 + xe)
    md = (out - r).abs().max().item()
    rd = md / (r.abs().max().item() + 1e-8)
    print(f"steps={steps} max_diff={md:.3e} rel={rd:.3e}")
