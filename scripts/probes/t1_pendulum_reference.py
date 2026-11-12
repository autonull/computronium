"""T1: is Pendulum's −1184 a budget limit or a harness defect?

The domain criterion is ``mean_reward > -200``. The harness measured −1184
after 400 episodes (TODO88 G15). The excluded possibility is that the
pipeline trains but 400 episodes is simply too few. This probe answers it
without touching the harness: a plain deterministic actor-critic (DDPG) with
the same environment, the same episode budget and the same deterministic
evaluation protocol.

Reference configuration (no sweeps):
- actor 3 → 64 → 64 → 1 (tanh × action bound), critic 4 → 64 → 64 → 1;
- replay 200k, batch 64, γ=0.99, τ=0.005, actor/critic lr 1e-3, grad clip 0.5;
- Gaussian exploration noise σ=0.15, 1 000 random warmup steps;
- 400 training episodes (the harness budget), then 1400 more to locate the
  episode count at which the criterion becomes reachable;
- deterministic evaluation over 20 episodes, seed 0.

Two policy-gradient references are recorded because both are defects, not
results: one-step TD without advantage normalization saturated tanh and
measured −1298 from episode 800 on, identical to 1e-8 across checkpoints;
PPO measured −1033 at 400 and −1146 at 1800 (random −1166) — its shared
gradient clip was dominated by a critic loss on raw returns, so the actor
never moved. DDPG trains a deterministic actor directly, which is the plain
actor-critic this ticket asks for.

Run: uv run python scripts/probes/t1_pendulum_reference.py
Measured (2026-11-12, RTX 3080 host CPU, ``T1_EPISODES=400``):
untrained actor −1312.5; **−123.6 at 400 episodes** (20 deterministic
evaluation episodes, seed 0). The criterion is reached at the harness budget,
so the budget is not the limit. The harness lane measured −6604 before the fix
and −133.9 after (``t1_pendulum_harness.py``).
"""

from __future__ import annotations

import json
import os
import random
import time
from collections import deque

import gymnasium as gym
import numpy as np
import torch
from torch import nn

__all__ = ["main"]

RESULTS: dict[str, object] = {
    "budget_episodes": 400,
    "reference_at_400": None,
    "reference_at_1800": None,
    "schedule": {},
}

GAMMA = 0.99
TAU = 0.005
LR = 1e-3
CLIP = 0.5
BATCH = 64
BUFFER = 200_000
WARMUP = 1_000
NOISE = 0.15
EVAL_EPISODES = 20


class Actor(nn.Module):
    def __init__(self, obs_dim: int, action_scale: float) -> None:
        super().__init__()
        self.scale = action_scale
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, states: torch.Tensor) -> torch.Tensor:
        return self.scale * torch.tanh(self.net(states))


class Critic(nn.Module):
    def __init__(self, obs_dim: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim + 1, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, states: torch.Tensor, actions: torch.Tensor) -> torch.Tensor:
        return self.net(torch.cat([states, actions], dim=-1))


def _tensor(obs: np.ndarray) -> torch.Tensor:
    return torch.as_tensor(obs, dtype=torch.float32).unsqueeze(0)


@torch.no_grad()
def evaluate(actor: Actor, env: gym.Env, episodes: int, seed: int) -> float:
    """Deterministic mean-action evaluation, the harness's protocol."""
    rewards: list[float] = []
    for episode in range(episodes):
        obs, _ = env.reset(seed=seed + episode)
        total = 0.0
        while True:
            action = actor(_tensor(obs))
            obs, reward, terminated, truncated, _ = env.step(
                action.numpy()[0].clip(-2.0, 2.0)
            )
            total += float(reward)
            if terminated or truncated:
                break
        rewards.append(total)
    return float(np.mean(rewards))


def _soft_update(target: nn.Module, source: nn.Module) -> None:
    with torch.no_grad():
        for target_param, param in zip(target.parameters(), source.parameters()):
            target_param.mul_(1.0 - TAU).add_(TAU * param)


def _update(
    actor: Actor,
    critic: Critic,
    actor_target: Actor,
    critic_target: Critic,
    actor_opt: torch.optim.Optimizer,
    critic_opt: torch.optim.Optimizer,
    batch: list[tuple],
) -> None:
    states, actions, rewards, next_states, dones = zip(*batch)
    states = torch.stack(states)
    actions = torch.stack(actions)
    rewards = torch.tensor(rewards, dtype=torch.float32).unsqueeze(-1)
    next_states = torch.stack(next_states)
    dones = torch.tensor(dones, dtype=torch.float32).unsqueeze(-1)

    with torch.no_grad():
        target = rewards + GAMMA * (1.0 - dones) * critic_target(
            next_states, actor_target(next_states)
        )
    critic_loss = 0.5 * (critic(states, actions) - target).pow(2).mean()
    critic_opt.zero_grad()
    critic_loss.backward()
    torch.nn.utils.clip_grad_norm_(critic.parameters(), CLIP)
    critic_opt.step()

    actor_loss = -critic(states, actor(states)).mean()
    actor_opt.zero_grad()
    actor_loss.backward()
    torch.nn.utils.clip_grad_norm_(actor.parameters(), CLIP)
    actor_opt.step()

    _soft_update(actor_target, actor)
    _soft_update(critic_target, critic)


def train(
    env: gym.Env,
    actor: Actor,
    critic: Critic,
    episodes: int,
    *,
    start: int,
    on_episode,
) -> None:
    actor_target = Actor(env.observation_space.shape[0], 2.0)
    critic_target = Critic(env.observation_space.shape[0])
    actor_target.load_state_dict(actor.state_dict())
    critic_target.load_state_dict(critic.state_dict())
    actor_opt = torch.optim.Adam(actor.parameters(), lr=LR)
    critic_opt = torch.optim.Adam(critic.parameters(), lr=LR)
    buffer: deque[tuple] = deque(maxlen=BUFFER)
    steps = 0

    for episode in range(start, start + episodes):
        obs, _ = env.reset(seed=episode)
        while True:
            state = _tensor(obs)
            if steps < WARMUP:
                action = torch.empty(1, 1).uniform_(-2.0, 2.0)
            else:
                with torch.no_grad():
                    action = actor(state) + NOISE * torch.randn(1, 1)
            next_obs, reward, terminated, truncated, _ = env.step(
                action.numpy()[0].clip(-2.0, 2.0)
            )
            done = float(terminated)
            buffer.append((
                state.squeeze(0),
                action.squeeze(0).detach(),
                float(reward),
                _tensor(next_obs).squeeze(0),
                done,
            ))
            steps += 1
            if steps >= WARMUP and len(buffer) >= BATCH:
                _update(
                    actor,
                    critic,
                    actor_target,
                    critic_target,
                    actor_opt,
                    critic_opt,
                    random.sample(buffer, BATCH),
                )
            obs = next_obs
            if terminated or truncated:
                break
        if int(os.environ.get("T1_DEBUG", "0")) and episode % 20 == 0:
            print(f"episode {episode}: steps={steps}", flush=True)
        on_episode(episode + 1)


def main() -> int:
    torch.manual_seed(0)
    np.random.seed(0)
    random.seed(0)
    env = gym.make("Pendulum-v1")
    eval_env = gym.make("Pendulum-v1")
    obs_dim = env.observation_space.shape[0]
    actor = Actor(obs_dim, 2.0)
    critic = Critic(obs_dim)
    started = time.perf_counter()
    total = int(os.environ.get("T1_EPISODES", "1800"))

    random_reward = evaluate(actor, eval_env, EVAL_EPISODES, seed=10_000)
    schedule: dict[str, float] = {"0 (untrained actor)": random_reward}
    checkpoints = {100, 200, 400, 800, 1200, 1800}

    def on_episode(episode: int) -> None:
        if episode in checkpoints:
            schedule[str(episode)] = evaluate(
                actor, eval_env, EVAL_EPISODES, seed=10_000
            )

    train(env, actor, critic, total, start=0, on_episode=on_episode)

    RESULTS["reference_at_400"] = schedule.get("400")
    RESULTS["reference_at_1800"] = schedule.get(str(total))
    RESULTS["schedule"] = schedule
    RESULTS["episodes_per_eval"] = EVAL_EPISODES
    RESULTS["walltime_s"] = round(time.perf_counter() - started, 1)
    print(json.dumps(RESULTS, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
