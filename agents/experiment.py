"""
Experiment baseline configuration for the AgentWorld task runner.

This module centralizes all the experimental "baseline" knobs that can be toggled
from the command line in agents/run.py. It deliberately keeps the default behavior
(LLM agents that broadcast plans via chat and see each other) unchanged: when no
flags are set, ExperimentConfig is a no-op.

Baselines / knobs (see agents/run.py --help):
  Behavior baselines:
    - single_agent_upper_bound : run the whole task with one solo merged agent
    - discussion_rounds N      : first N rounds chat-only, then communication cut
    - no_communication         : communication cut from round 1
    - shared_plan_only         : communication cut, but a shared plan is injected
    - random_agent             : skip the LLM, take uniformly random legal actions
  Design knobs (combinable with any baseline):
    - max_rounds               : override the round budget (CLI > task YAML > 55)
    - no_roles                 : present generic identity + "self-organize" directive
    - random_spawn             : seeded random spawn locations
    - no_task_docs             : drop the task-specific relevant_game_context
    - seed                     : seed RNG for random_spawn / random_agent

"Communication" here means: the chat tool, the transfer_items tool, chat history,
and the visibility of other players (PARTY AGENT STATUS block + the `players` array
in observations). Cutting communication removes all of these.
"""

import json
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_MAX_ROUNDS = 55


@dataclass
class ExperimentConfig:
    """Holds all baseline/knob flags for a run. A default-constructed instance is a no-op."""

    # Behavior baselines
    single_agent_upper_bound: bool = False
    discussion_rounds: int = 0
    no_communication: bool = False
    shared_plan_only: bool = False
    random_agent: bool = False

    # Design knobs
    max_rounds: Optional[int] = None
    no_roles: bool = False
    random_spawn: bool = False
    spawn_region: Optional[Tuple[int, int, int, int]] = None  # (x1, y1, x2, y2)
    no_task_docs: bool = False
    seed: Optional[int] = None

    rng: random.Random = field(default_factory=random.Random, repr=False)

    @classmethod
    def from_args(cls, args) -> "ExperimentConfig":
        spawn_region = None
        if getattr(args, "spawn_region", None):
            spawn_region = tuple(int(v) for v in args.spawn_region)  # type: ignore[assignment]

        seed = getattr(args, "seed", None)
        cfg = cls(
            single_agent_upper_bound=getattr(args, "single_agent_upper_bound", False),
            discussion_rounds=getattr(args, "discussion_rounds", 0) or 0,
            no_communication=getattr(args, "no_communication", False),
            shared_plan_only=getattr(args, "shared_plan_only", False),
            random_agent=getattr(args, "random_agent", False),
            max_rounds=getattr(args, "max_rounds", None),
            no_roles=getattr(args, "no_roles", False),
            random_spawn=getattr(args, "random_spawn", False),
            spawn_region=spawn_region,
            no_task_docs=getattr(args, "no_task_docs", False),
            seed=seed,
            rng=random.Random(seed),
        )
        return cfg

    def validate(self) -> None:
        """Raise ValueError on conflicting flag combinations."""
        comm_baselines = [
            ("--no-communication", self.no_communication),
            ("--discussion-rounds", self.discussion_rounds > 0),
            ("--shared-plan-only", self.shared_plan_only),
        ]
        active = [name for name, on in comm_baselines if on]
        if len(active) > 1:
            raise ValueError(
                f"Communication baselines are mutually exclusive, got: {', '.join(active)}"
            )
        if self.discussion_rounds < 0:
            raise ValueError("--discussion-rounds must be >= 0")
        if self.max_rounds is not None and self.max_rounds <= 0:
            raise ValueError("--max-rounds must be > 0")
        if self.spawn_region is not None and not self.random_spawn:
            raise ValueError("--spawn-region requires --random-spawn")

    # ---- derived helpers -------------------------------------------------

    @property
    def cuts_communication(self) -> bool:
        """True if the steady-state (post-discussion) has communication disabled."""
        return (
            self.single_agent_upper_bound
            or self.no_communication
            or self.shared_plan_only
            or self.discussion_rounds > 0
        )

    def resolve_max_rounds(self, task_rounds: Optional[int]) -> int:
        """Precedence: CLI --max-rounds > task YAML rounds > DEFAULT_MAX_ROUNDS."""
        if self.max_rounds is not None:
            return self.max_rounds
        if task_rounds:
            return int(task_rounds)
        return DEFAULT_MAX_ROUNDS

    # ---- agent restriction application -----------------------------------

    @staticmethod
    def _base(agent):
        """Resolve the real BaseAgent under a possible ConfigurableAgent wrapper."""
        return getattr(agent, "base_agent", agent)

    def apply_agent_restrictions(
        self,
        agent,
        *,
        allow_chat: bool,
        allow_transfer: bool,
        hide_chat_history: bool,
        hide_other_players: bool,
        discussion_phase: bool = False,
    ) -> None:
        """Set communication restriction flags on an agent and rebuild its tool list."""
        base = self._base(agent)
        base.allow_chat = allow_chat
        base.allow_transfer = allow_transfer
        base.hide_chat_history = hide_chat_history
        base.hide_other_players = hide_other_players
        base.discussion_phase = discussion_phase
        base._rebuild_tools()

    def steady_state_restrictions(self) -> Dict[str, bool]:
        """The restriction kwargs that apply once any discussion phase is over."""
        cut = self.cuts_communication
        return {
            "allow_chat": not cut,
            "allow_transfer": not cut,
            "hide_chat_history": cut,
            "hide_other_players": cut,
            "discussion_phase": False,
        }

    # ---- single-agent upper bound ----------------------------------------

    def collapse_to_single_agent(self, task_config) -> None:
        """Turn a multi-agent task into one solo agent_1, in place.

        The run has exactly one participant for the whole task; no other agents are
        spawned and communication tools are disabled by steady_state_restrictions().
        To make the solo upper bound feasible, skills are max-merged, inventory is
        summed, and equipment is unioned. Location / username / new_character are
        taken from the first agent.
        """
        agents = task_config.agents
        if len(agents) <= 1:
            return

        ordered = [agents[k] for k in sorted(agents.keys())]
        primary = dict(ordered[0])

        merged_skills: Dict[str, int] = {}
        merged_inv: Dict[str, Dict[str, Any]] = {}
        merged_equip: Dict[str, Dict[str, Any]] = {}

        for adata in ordered:
            for skill, level in (adata.get("skill_levels") or {}).items():
                merged_skills[skill] = max(merged_skills.get(skill, 0), int(level))
            for item in (adata.get("inventory_items") or []):
                key = item["item"]
                if key in merged_inv:
                    merged_inv[key]["count"] += item.get("count", 1)
                else:
                    merged_inv[key] = dict(item)
            for item in (adata.get("equipped_items") or []):
                key = item["item"]
                # Keep the highest enchant when the same item is equipped by multiple agents.
                if key not in merged_equip or item.get("enchant", 0) > merged_equip[key].get("enchant", 0):
                    merged_equip[key] = dict(item)

        primary["skill_levels"] = merged_skills
        primary["inventory_items"] = list(merged_inv.values())
        primary["equipped_items"] = list(merged_equip.values())

        task_config.agents = {"agent_1": primary}

    # ---- random spawn ----------------------------------------------------

    def random_location(self, base_locations: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Pick a seeded random spawn coordinate.

        Uses --spawn-region if provided, otherwise jitters within the bounding box of
        the task's configured spawn points (with a small margin).
        """
        if self.spawn_region is not None:
            x1, y1, x2, y2 = self.spawn_region
            return (self.rng.randint(min(x1, x2), max(x1, x2)),
                    self.rng.randint(min(y1, y2), max(y1, y2)))

        if base_locations:
            xs = [x for x, _ in base_locations]
            ys = [y for _, y in base_locations]
            margin = 5
            return (self.rng.randint(min(xs) - margin, max(xs) + margin),
                    self.rng.randint(min(ys) - margin, max(ys) + margin))

        # No reference points: fall back to a small area around origin-ish spawn.
        return (self.rng.randint(380, 400), self.rng.randint(1, 10))


class RandomAgentPolicy:
    """A non-LLM agent that takes a uniformly random *legal* action each turn.

    "Legal" = an action whose preconditions are satisfiable from the current
    observation (e.g. only harvest resources / attack mobs that are actually
    visible, only equip items that are equippable and present in inventory).

    The returned string mimics the markers produced by BaseAgent.execute_single_tool_call
    ([TOOL_CALL_INFO] / [TOOL_RESULT]) so the runner's trajectory parsing, chat
    detection and complete detection keep working unchanged.
    """

    def __init__(self, experiment: ExperimentConfig):
        self.experiment = experiment
        self.rng = experiment.rng

    def act(self, console) -> str:
        agent = ExperimentConfig._base(console.agent)
        game = agent.game_tools

        # Refresh observation so candidate actions reflect the current world state.
        try:
            game.observe_environment({"radius": 64})
        except Exception:
            pass
        obs = game.get_last_observation_data() or {}

        candidates = self._build_candidates(obs, agent)
        if not candidates:
            candidates = [("sleep", {"seconds": 1}, game.sleep)]

        name, args, fn = self.rng.choice(candidates)
        try:
            result = fn(args)
        except Exception as e:
            result = f"Error executing {name}: {e}"

        args_display = ", ".join(f"{k}={v}" for k, v in args.items())
        return f"[random-agent]\n[TOOL_CALL_INFO] {name}({args_display})\n[TOOL_RESULT] {result}"

    def _build_candidates(self, obs: Dict[str, Any], agent) -> List[Tuple[str, Dict[str, Any], Any]]:
        game = agent.game_tools
        candidates: List[Tuple[str, Dict[str, Any], Any]] = []

        loc = obs.get("location", {}) or {}
        cx, cy = loc.get("x"), loc.get("y")

        # Move to a random nearby tile.
        if cx is not None and cy is not None:
            tx = cx + self.rng.randint(-8, 8)
            ty = cy + self.rng.randint(-8, 8)
            candidates.append(("move_character", {"x": tx, "y": ty}, game.move_character))

        # Harvest any visible resource.
        for bucket in ("trees", "rocks", "fishSpots", "foraging"):
            for res in obs.get(bucket, []) or []:
                inst = res.get("instance")
                if inst is not None:
                    candidates.append(
                        ("harvest_resource", {"targetInstance": str(inst)}, game.harvest_resource)
                    )

        # Attack any visible mob.
        for mob in obs.get("mobs", []) or []:
            inst = mob.get("instance")
            if inst is not None:
                candidates.append(
                    ("attack_entity", {"targetInstance": str(inst)}, game.attack_entity)
                )

        # Equip any equippable inventory item (by slot index).
        items = (obs.get("inventory", {}) or {}).get("items", []) or []
        for idx, item in enumerate(items):
            if item.get("equippable"):
                candidates.append(("equip_item", {"index": idx}, game.equip_item))

        # Always-available no-op.
        candidates.append(("sleep", {"seconds": 1}, game.sleep))

        # Communication actions only when comms are allowed for this agent.
        if getattr(agent, "allow_chat", True):
            candidates.append(
                ("chat", {"message": "..."}, game.chat)
            )
        if getattr(agent, "allow_transfer", True):
            players = obs.get("players", []) or []
            if players and items:
                target = self.rng.choice(players).get("name")
                item = self.rng.choice(items)
                if target and item.get("key"):
                    candidates.append((
                        "transfer_items",
                        {"targetPlayer": target, "itemKey": item["key"], "count": 1},
                        game.transfer_items,
                    ))

        return candidates
