"""
Beam Search Task Verification for AgentWorld Multi-Agent Benchmark.

This package implements a beam search-based verification mechanism that uses
Claude CLI to propose actions for multi-agent benchmark tasks, simulates
execution via the simulation API, and verifies success using Python verifiers.
"""

from .task_loader import load_task, task_to_initial_states, TaskConfig
from .simulation_client import SimulationClient
from .action_proposer import propose_actions
from .verifier_adapter import states_to_trajectory, verify_task
from .branch_evaluator import evaluate_branches
from .beam_search import BeamSearchVerifier, BranchState, VerificationResult

__all__ = [
    'load_task',
    'task_to_initial_states',
    'TaskConfig',
    'SimulationClient',
    'propose_actions',
    'states_to_trajectory',
    'verify_task',
    'evaluate_branches',
    'BeamSearchVerifier',
    'BranchState',
    'VerificationResult',
]
