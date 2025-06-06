"""Civ 8 - Hegemon AI Prototype (Phase 2+)"""

from __future__ import annotations

import random
from typing import Dict, List, Callable, Any, Tuple

try:
    from rich.console import Console
    from rich.table import Table

    console = Console()
    USE_RICH = True
except Exception:  # pragma: no cover - rich might not be installed
    console = None
    USE_RICH = False


    """Represents a single civilization and its state."""

    def __init__(self, name: str, base: int, boosts: Dict[str, int] | None = None):

        self.influence_over: Dict[str, int] = {}
        self.unrest_index = 0

    def get_influence_status(self, score: int) -> str:
        if score >= 80:
            return "Integrated"
        if score >= 60:
            return "Vassalized"
        if score >= 40:
            return "Trade Partner"
        if score >= 20:
            return "Cultural Affinity"
        return "None"


class Game:
    """Manages the entire game state."""

    def __init__(self) -> None:
        self.player, self.opponents = self._init_civs()
        for opp in self.opponents:
            self.player.influence_over[opp.name] = 0
        self.objectives = self._init_objectives()
        self.is_running = True
        self.turn = 1

    # ------------------------------------------------------------------
    # Initialization helpers
    def _init_civs(self) -> Tuple[Civilization, List[Civilization]]:
        player_boosts = {
            "Innovation & Tech Leadership": 55,
            "Military Strength & Tech Edge": 55,
            "Reserve-Currency / Monetary Influence": 55,
        }
        player = Civilization("Player Civ", 50, player_boosts)

        opp1 = Civilization("Neo-Rome", 45, {"Economic Size": 48})
        opp2 = Civilization("Vultari Collective", 46, {"Military Strength & Tech Edge": 50})

        return player, [opp1, opp2]

    def _init_objectives(self) -> Dict[str, Dict[str, Any]]:
        def trade_route(g: Game) -> bool:
            target = g.opponents[0]  # Neo-Rome
            status = g.player.get_influence_status(g.player.influence_over[target.name])
            return status == "Trade Partner" and g.player.pillars["Share of World Trade"] > 55

        def cultural_asc(g: Game) -> bool:
            target = g.opponents[0]
            return g.player.influence_over[target.name] > 40 or target.pillars["Social Cohesion & Wellbeing"] < 40

        def regional_resources(g: Game) -> bool:
            return g.objectives["Secure Regional Resources"].get("achieved_by_action", False)

        return {
            "Establish Dominant Trade Route": {"status": "Not Started", "check": trade_route},
            "Achieve Cultural Ascendancy": {"status": "Not Started", "check": cultural_asc},
            "Secure Regional Resources": {"status": "Not Started", "check": regional_resources},
        }

    # ------------------------------------------------------------------
    # Display helpers
    def display_status(self) -> None:
        if USE_RICH:
            table = Table(title=f"{self.player.name} - Turn {self.turn} - Kardashev Tier {self.player.kardashev_tier}")
            table.add_column("Pillar")
            table.add_column("Value", justify="right")
            for k, v in self.player.pillars.items():
                table.add_row(k, str(v))
            table.add_row("Net Energy Output", str(self.player.net_energy_output))
            console.print(table)
            for opp in self.opponents:
                score = self.player.influence_over[opp.name]
                status = self.player.get_influence_status(score)
                console.print(
                    f"[bold]{opp.name}[/bold] stance: {opp.stance} | Influence: {status} ({score}) | Unrest: {opp.unrest_index}"
                )
            console.print("-" * 20)
        else:
            print(f"\n{self.player.name} - Turn {self.turn} - Kardashev Tier {self.player.kardashev_tier}")
            for k, v in self.player.pillars.items():
                print(f"  {k}: {v}")
            print(f"  Net Energy Output: {self.player.net_energy_output}")
            for opp in self.opponents:
                score = self.player.influence_over[opp.name]
                status = self.player.get_influence_status(score)
                print(f"Influence over {opp.name}: {status} ({score}) | {opp.name} stance: {opp.stance} | Unrest: {opp.unrest_index}")
            print("-" * 20)

    def display_objectives(self) -> None:
        print("Hegemonic Objectives:")
        for name, data in self.objectives.items():
            print(f"  {name}: {data['status']}")
        print()

    # ------------------------------------------------------------------
    # Core game mechanics
    def check_objectives(self) -> None:
        for name, data in self.objectives.items():
            if data["status"] != "Achieved" and data["check"](self):
                data["status"] = "Achieved"
                print(f"[Objective Achieved: {name}]")

    def check_kardashev_progress(self) -> None:
        if self.player.kardashev_tier != 0:
            return
        keys = [
            "Innovation & Tech Leadership",
            "Economic Size",
            "Reserve-Currency / Monetary Influence",
        ]
        avg = sum(self.player.pillars[k] for k in keys) / len(keys)
        if (
            all(obj["status"] == "Achieved" for obj in self.objectives.values())
            and self.player.net_energy_output > 500
            and avg > 70
        ):
            self.player.kardashev_tier = 1
            print("\n*** Congratulations! You have advanced to Kardashev Tier 1. ***\n")

    def _choose_opp_invest_pillar(self, opp: Civilization) -> str:
        if self.player.influence_over[opp.name] > 30:
            if opp.pillars["Social Cohesion & Wellbeing"] < 60:
                return "Social Cohesion & Wellbeing"
            return "Military Strength & Tech Edge"
        return min(PILLAR_NAMES, key=lambda p: opp.pillars[p])

    def opponent_turn(self) -> None:
        for opp in self.opponents:
            target = self._choose_opp_invest_pillar(opp)
            opp.pillars[target] = min(opp.pillars[target] + 3, 100)
            opp.pillars["Economic Size"] = max(opp.pillars["Economic Size"] - 2, 0)
            if USE_RICH:
                console.print(f"[cyan]{opp.name} invests in {target}.[/cyan]")
            else:
                print(f"{opp.name} invests in {target}.")

    def trigger_event(self) -> None:
        if random.random() > 0.25:
            return
        event = random.choice(EVENTS)
        print(f"\n[Event Triggered: {event['name']}] {event['description']}")
        event["effect"](self)

    def end_turn(self) -> None:
        print("\n--- End of Turn ---")
        self.trigger_event()
        self.opponent_turn()
        self.turn += 1
        self.check_objectives()
        self.check_kardashev_progress()
        self.display_status()
        self.display_objectives()
        print(f"--- Beginning Turn {self.turn} ---")

    # ------------------------------------------------------------------
    # Helpers for command handlers
    def get_opponent(self, name: str) -> Civilization | None:
        name = name.lower()
        for opp in self.opponents:
            if opp.name.lower() == name:
                return opp
        return None


# ----------------------------------------------------------------------
# Event definitions
def _event_tech_breakthrough(game: Game) -> None:
    civs = [game.player] + game.opponents
    civ = max(civs, key=lambda c: c.pillars["Innovation & Tech Leadership"])
    civ.pillars["Innovation & Tech Leadership"] = min(civ.pillars["Innovation & Tech Leadership"] + 5, 100)
    print(f"{civ.name} experiences a surge in innovation!")


def _event_economic_boom(game: Game) -> None:
    for civ in [game.player] + game.opponents:
        civ.pillars["Economic Size"] = min(civ.pillars["Economic Size"] + 3, 100)
    print("Regional economies surge with new opportunities.")


def _event_solar_flare(game: Game) -> None:
    for civ in [game.player] + game.opponents:
        civ.net_energy_output = max(civ.net_energy_output - 10, 0)
    print("A solar flare disrupts energy production across civilizations.")


EVENTS = [
    {
        "name": "Technological Breakthrough",
        "description": "A sudden leap in knowledge boosts innovation.",
        "effect": _event_tech_breakthrough,
    },
    {
        "name": "Economic Boom",
        "description": "Market optimism increases economic size for all.",
        "effect": _event_economic_boom,
    },
    {
        "name": "Solar Flare Disruptions",
        "description": "A solar flare lowers net energy output this turn.",
        "effect": _event_solar_flare,
    },
]
# ----------------------------------------------------------------------
# Command Handlers
def handle_invest(game: Game, args: List[str]) -> str:
    if not args:
        return "Please specify which pillar to invest in."
    pillar_name = " ".join(args).title()
    matched = next((p for p in PILLAR_NAMES if p.lower() == pillar_name.lower()), None)
    if not matched:
        return f"Pillar '{pillar_name}' not recognized."

    game.player.pillars[matched] = min(game.player.pillars[matched] + 5, 100)
    game.player.pillars["Economic Size"] = max(game.player.pillars["Economic Size"] - 2, 0)
    if matched in ["Innovation & Tech Leadership", "Financial-Center & Capital-Market Depth"]:
        game.player.net_energy_output = max(game.player.net_energy_output - 1, 0)
    return f"Investment allocated to {matched}. Our economic size has been slightly impacted."


def handle_cultural_broadcast(game: Game, args: List[str]) -> str:
    if not args:
        return "Specify a target civilization for the broadcast."
    target = game.get_opponent(args[0])
    if not target:
        return "Target not recognized."

    print("(Advisor: Planning cultural broadcast. This aims to increase our cultural influence.)")
    game.player.pillars["Economic Size"] = max(game.player.pillars["Economic Size"] - 3, 0)
    game.player.net_energy_output = max(game.player.net_energy_output - 5, 0)
    game.player.influence_over[target.name] = min(game.player.influence_over[target.name] + 5, 100)
    target.pillars["Social Cohesion & Wellbeing"] = max(target.pillars["Social Cohesion & Wellbeing"] - 2, 0)
    return f"Cultural broadcast sent to {target.name}."


def handle_trade_deal(game: Game, args: List[str]) -> str:
    if not args:
        return "Specify a target civilization for the trade deal."
    target = game.get_opponent(args[0])
    if not target:
        return "Target not recognized."
    if target.stance == "Hostile":
        return f"{target.name} is hostile and refuses trade talks."

    print("(Advisor: Proposing trade deal to strengthen our economies.)")
    game.player.pillars["Economic Size"] = max(game.player.pillars["Economic Size"] - 2, 0)
    game.player.influence_over[target.name] = min(game.player.influence_over[target.name] + 10, 100)
    game.player.pillars["Share of World Trade"] = min(game.player.pillars["Share of World Trade"] + 5, 100)
    game.player.pillars["Economic Size"] = min(game.player.pillars["Economic Size"] + 2, 100)
    target.pillars["Share of World Trade"] = min(target.pillars["Share of World Trade"] + 3, 100)
    target.pillars["Economic Size"] = min(target.pillars["Economic Size"] + 1, 100)
    return f"{target.name} has accepted our trade deal! Our economies are now more linked."


def handle_military_power(game: Game, args: List[str]) -> str:
    if not args:
        return "Specify a target civilization."
    target = game.get_opponent(args[0])
    if not target:
        return "Target not recognized."
    if game.player.pillars["Military Strength & Tech Edge"] <= target.pillars["Military Strength & Tech Edge"]:
        return "Our military strength is insufficient to project power effectively."

    print("(Advisor: Deploying forces to demonstrate our resolve.)")
    game.player.net_energy_output = max(game.player.net_energy_output - 10, 0)
    game.player.pillars["Economic Size"] = max(game.player.pillars["Economic Size"] - 4, 0)
    game.player.pillars["Share of World Trade"] = min(game.player.pillars["Share of World Trade"] + 3, 100)
    target.unrest_index = min(target.unrest_index + 5, 100)
    target.stance = "Wary"
    game.objectives["Secure Regional Resources"]["achieved_by_action"] = True
    return f"Our forces demonstrate power near {target.name}. They are now Wary."


def handle_quit(game: Game, args: List[str]) -> str:
    game.is_running = False
    return "Exiting simulation. The fate of your civilization rests."


COMMAND_DISPATCHER: Dict[str, Callable[[Game, List[str]], str]] = {
    "invest": handle_invest,
    "status": lambda g, a: (g.display_status() or ""),
    "objectives": lambda g, a: (g.display_objectives() or ""),
    "broadcast": handle_cultural_broadcast,
    "trade": handle_trade_deal,
    "military": handle_military_power,
    "end": lambda g, a: (g.end_turn() or ""),
    "quit": handle_quit,
    "exit": handle_quit,
}
def main() -> None:
    game = Game()
    print("Welcome to Civ 8 - Hegemon AI Prototype (Phase 2+)")
    game.display_status()
    game.display_objectives()
    while game.is_running:
            raw_input = input("\nCommand: ").lower().strip()
            print("\nSimulation ended by user.")
        if not raw_input:
            continue
        parts = raw_input.split()
        command = parts[0]
        args = parts[1:]

        handler = COMMAND_DISPATCHER.get(command)
        if handler:
            result = handler(game, args)
            if result:
                print(result)
        else:
            print("I don't understand that command.")

if __name__ == "__main__":  # pragma: no cover

    elif cmd == "propose favorable trade deal to neo-rome":
        trade_deal(player, opponent)
    elif cmd == "offer financial aid to neo-rome":
        financial_aid(player, opponent)
    elif cmd == "project military power near neo-rome's borders":
        project_military_power(player, opponent)
    elif cmd == "begin joint research venture with neo-rome":
        research_venture(player, opponent)
    elif cmd in ["end turn", "end"]:
        check_objectives(player, opponent)
        print_status(player, opponent)
        show_objectives()
        check_kardashev_progress(player)
    elif cmd in ["quit", "exit"]:
        return False
    else:
        print("I don't understand that command.")
    return True


def main():
    player, opponent = init_civs()
    print("Welcome to Civ 8 - Hegemon AI Prototype (Phase 2)")
    print_status(player, opponent)
    show_objectives()
    while True:
        try:
            command = input("\nCommand: ")
        except EOFError:
            break
        if not take_turn(command, player, opponent):
            break


if __name__ == "__main__":
    main()
