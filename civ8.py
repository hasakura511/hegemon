# Civ 8 - Hegemon AI Prototype (Phase 2)
# Simulates Dalio Power Pillars, influence, and simple hegemonic actions

from typing import Dict, List

PILLAR_NAMES = [
    "Education & Human Capital",
    "Competitiveness & Productivity",
    "Innovation & Tech Leadership",
    "Economic Size",
    "Share of World Trade",
    "Military Strength & Tech Edge",
    "Financial-Center & Capital-Market Depth",
    "Reserve-Currency / Monetary Influence",
    "Social Cohesion & Wellbeing",
]

class Civilization:
    def __init__(self, name: str, base: int, boosts: Dict[str, int] = None):
        self.name = name
        self.pillars: Dict[str, int] = {p: base for p in PILLAR_NAMES}
        boosts = boosts or {}
        for k, v in boosts.items():
            if k in self.pillars:
                self.pillars[k] = v
        self.kardashev_tier = 0
        self.influence_over_opponent = 0  # 0-100 numeric score
        self.influence_status = "None"
        self.stance = "Neutral"
        self.net_energy_output = 100
        self.unrest_index = 0  # primarily for opponent

    def pillar_avg(self, keys: List[str]) -> float:
        return sum(self.pillars[k] for k in keys) / len(keys)


def init_civs():
    player_boosts = {
        "Innovation & Tech Leadership": 55,
        "Military Strength & Tech Edge": 55,
        "Reserve-Currency / Monetary Influence": 55,
    }
    player = Civilization("Player Civ", 50, player_boosts)

    opponent_boosts = {
        "Economic Size": 45,
        "Military Strength & Tech Edge": 48,
    }
    opponent = Civilization("Neo-Rome", 45, opponent_boosts)
    opponent.stance = "Neutral"
    return player, opponent


OBJECTIVES = {
    "Trade Route with Neo-Rome": "Not Started",
    "Cultural Ascendancy over Neo-Rome": "Not Started",
    "Secure Regional Resources": "Not Started",
}


def print_status(player: Civilization, opponent: Civilization):
    print(f"\n{player.name} - Kardashev Tier {player.kardashev_tier}")
    for k, v in player.pillars.items():
        print(f"  {k}: {v}")
    print(f"  Net Energy Output: {player.net_energy_output}")
    print(f"Influence over {opponent.name}: {player.influence_status} ({player.influence_over_opponent})")
    print(f"{opponent.name} stance: {opponent.stance}")
    print()


def show_objectives():
    print("Hegemonic Objectives:")
    for name, status in OBJECTIVES.items():
        print(f"  {name}: {status}")
    print()


def update_influence_status(player: Civilization):
    score = player.influence_over_opponent
    if score >= 60:
        player.influence_status = "Vassalized"
    elif score >= 40:
        player.influence_status = "Trade Partner"
    elif score >= 20:
        player.influence_status = "Cultural Affinity"
    else:
        player.influence_status = "None"


def invest(pillar: str, player: Civilization):
    if pillar not in player.pillars:
        print("I don't recognize that pillar.")
        return
    print(f"Investment allocated to {pillar}. This will slightly impact our economic size.")
    player.pillars[pillar] = min(player.pillars[pillar] + 5, 100)
    player.pillars["Economic Size"] = max(player.pillars["Economic Size"] - 2, 0)
    if pillar in (
        "Innovation & Tech Leadership",
        "Financial-Center & Capital-Market Depth",
    ):
        player.net_energy_output = max(player.net_energy_output - 1, 0)


def cultural_broadcast(player: Civilization, opponent: Civilization):
    print("Planning cultural broadcast to Neo-Rome. This aims to increase our cultural influence and potentially sway their public opinion. It will require economic resources.")
    player.pillars["Economic Size"] = max(player.pillars["Economic Size"] - 3, 0)
    player.net_energy_output = max(player.net_energy_output - 5, 0)
    player.influence_over_opponent = min(player.influence_over_opponent + 5, 100)
    opponent.pillars["Social Cohesion & Wellbeing"] = max(opponent.pillars["Social Cohesion & Wellbeing"] - 2, 0)
    print("Cultural broadcast sent. Our narratives are reaching Neo-Rome.")
    update_influence_status(player)
    if OBJECTIVES["Cultural Ascendancy over Neo-Rome"] == "Not Started":
        OBJECTIVES["Cultural Ascendancy over Neo-Rome"] = "In Progress"


def trade_deal(player: Civilization, opponent: Civilization):
    if opponent.stance == "Hostile":
        print("Neo-Rome is hostile and refuses trade talks.")
        return
    print("Planning trade deal with Neo-Rome. This aims to boost our economies and establish a trade partnership. It will require some initial economic investment.")
    player.pillars["Economic Size"] = max(player.pillars["Economic Size"] - 2, 0)
    player.influence_over_opponent = min(player.influence_over_opponent + 10, 100)
    player.pillars["Share of World Trade"] = min(player.pillars["Share of World Trade"] + 5, 100)
    player.pillars["Economic Size"] = min(player.pillars["Economic Size"] + 2, 100)
    opponent.pillars["Share of World Trade"] = min(opponent.pillars["Share of World Trade"] + 3, 100)
    opponent.pillars["Economic Size"] = min(opponent.pillars["Economic Size"] + 1, 100)
    print("Neo-Rome has accepted our trade deal! Our economies are now more linked.")
    update_influence_status(player)
    if OBJECTIVES["Trade Route with Neo-Rome"] == "Not Started":
        OBJECTIVES["Trade Route with Neo-Rome"] = "In Progress"
    if player.influence_status == "Trade Partner" and player.pillars["Share of World Trade"] > 55:
        OBJECTIVES["Trade Route with Neo-Rome"] = "Achieved"


def financial_aid(player: Civilization, opponent: Civilization):
    if player.pillars["Reserve-Currency / Monetary Influence"] <= 60:
        print("Our monetary influence is too low to offer effective aid.")
        return
    print("Financial aid package dispatched. This should strengthen Neo-Rome's economy and our monetary influence.")
    player.pillars["Economic Size"] = max(player.pillars["Economic Size"] - 5, 0)
    player.pillars["Financial-Center & Capital-Market Depth"] = max(player.pillars["Financial-Center & Capital-Market Depth"] - 1, 0)
    player.influence_over_opponent = min(player.influence_over_opponent + 8, 100)
    opponent.pillars["Economic Size"] = min(opponent.pillars["Economic Size"] + 3, 100)
    update_influence_status(player)


def project_military_power(player: Civilization, opponent: Civilization):
    if player.pillars["Military Strength & Tech Edge"] <= opponent.pillars["Military Strength & Tech Edge"]:
        print("Our military strength is insufficient to project power effectively.")
        return
    print("Our forces are making a clear statement near Neo-Rome. This should secure our interests.")
    player.net_energy_output = max(player.net_energy_output - 10, 0)
    player.pillars["Economic Size"] = max(player.pillars["Economic Size"] - 4, 0)
    player.pillars["Share of World Trade"] = min(player.pillars["Share of World Trade"] + 3, 100)
    opponent.unrest_index = min(opponent.unrest_index + 5, 100)
    opponent.stance = "Wary"
    if OBJECTIVES["Secure Regional Resources"] != "Achieved":
        OBJECTIVES["Secure Regional Resources"] = "Achieved"
    update_influence_status(player)


def research_venture(player: Civilization, opponent: Civilization):
    print("Beginning joint research venture with Neo-Rome.")
    player.net_energy_output = max(player.net_energy_output - 2, 0)
    player.pillars["Economic Size"] = max(player.pillars["Economic Size"] - 2, 0)
    player.pillars["Innovation & Tech Leadership"] = min(player.pillars["Innovation & Tech Leadership"] + 5, 100)
    opponent.pillars["Innovation & Tech Leadership"] = min(opponent.pillars["Innovation & Tech Leadership"] + 3, 100)
    player.influence_over_opponent = min(player.influence_over_opponent + 3, 100)
    print("Research collaboration underway. Both civilizations benefit from new knowledge.")
    update_influence_status(player)


def check_objectives(player: Civilization, opponent: Civilization):
    if OBJECTIVES["Cultural Ascendancy over Neo-Rome"] != "Achieved":
        if player.influence_over_opponent > 40 or opponent.pillars["Social Cohesion & Wellbeing"] < 40:
            OBJECTIVES["Cultural Ascendancy over Neo-Rome"] = "Achieved"
    if OBJECTIVES["Trade Route with Neo-Rome"] == "In Progress":
        if player.influence_status == "Trade Partner" and player.pillars["Share of World Trade"] > 55:
            OBJECTIVES["Trade Route with Neo-Rome"] = "Achieved"


def check_kardashev_progress(player: Civilization):
    keys = ["Innovation & Tech Leadership", "Economic Size", "Reserve-Currency / Monetary Influence"]
    avg = player.pillar_avg(keys)
    if (
        all(status == "Achieved" for status in OBJECTIVES.values())
        and player.net_energy_output > 500
        and avg > 70
        and player.kardashev_tier == 0
    ):
        player.kardashev_tier = 1
        print("\n*** Congratulations! You have advanced to Kardashev Tier 1. ***\n")


def take_turn(command: str, player: Civilization, opponent: Civilization):
    cmd = command.lower()
    if cmd in ["what's our status?", "status report", "status"]:
        print_status(player, opponent)
    elif cmd == "display hegemonic objectives":
        show_objectives()
    elif cmd.startswith("invest in "):
        pillar = command[len("invest in "):].strip().title()
        matched = next((p for p in PILLAR_NAMES if p.lower() == pillar.lower()), None)
        if matched:
            invest(matched, player)
        else:
            print("I don't recognize that pillar.")
    elif cmd == "initiate cultural broadcast to neo-rome":
        cultural_broadcast(player, opponent)
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
