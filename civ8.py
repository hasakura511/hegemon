# Civ 8 - Hegemon AI Prototype
# Simulates core Dalio Power Pillars and a simple LLM Advisor interaction.

PILLARS = {
    "Education & Human Capital": 50,
    "Competitiveness & Productivity": 50,
    "Innovation & Tech Leadership": 50,
    "Economic Size": 50,
    "Share of World Trade": 50,
    "Military Strength & Tech Edge": 50,
    "Financial-Center & Capital-Market Depth": 50,
    "Reserve-Currency / Monetary Influence": 50,
}

SUGGESTIONS = {
    "Education & Human Capital": "Investing in schools could improve our human capital.",
    "Competitiveness & Productivity": "Improving infrastructure may boost productivity.",
    "Innovation & Tech Leadership": "Funding research initiatives can spur innovation.",
    "Economic Size": "Encouraging trade may expand our economy.",
    "Share of World Trade": "Negotiating trade deals could increase our market share.",
    "Military Strength & Tech Edge": "Modernizing equipment might strengthen the military.",
    "Financial-Center & Capital-Market Depth": "Developing banking systems could deepen markets.",
    "Reserve-Currency / Monetary Influence": "Strengthening monetary policy may raise influence.",
}

def print_pillars():
    for name, value in PILLARS.items():
        print(f"{name}: {value}")


def status():
    print("Current Dalio Power Pillars:")
    print_pillars()
    # Suggest improvement for the lowest pillar
    lowest = min(PILLARS, key=PILLARS.get)
    suggestion = SUGGESTIONS.get(lowest, "No suggestion available.")
    print(f"Your {lowest} is {PILLARS[lowest]}. {suggestion}")


def invest(pillar_name):
    if pillar_name in PILLARS:
        PILLARS[pillar_name] = min(PILLARS[pillar_name] + 5, 100)
        PILLARS["Economic Size"] = max(PILLARS["Economic Size"] - 2, 0)
        print(f"Investing in {pillar_name}. This will slightly impact our economic size.")
    else:
        print("I don't recognize that pillar.")


def main():
    print("Initial Dalio Power Pillars:")
    print_pillars()
    while True:
        command = input("\nPlayer Command: ").strip().lower()
        if command in ["what's our status?", "whats our status?", "status"]:
            status()
        elif command.startswith("invest in "):
            name_input = command[len("invest in "):].strip().title()
            # Match to pillar names case-insensitively
            matched = next((n for n in PILLARS if n.lower() == name_input.lower()), None)
            if matched:
                invest(matched)
            else:
                print("I don't recognize that pillar.")
        elif command in ["end turn", "end", "next"]:
            print("Updated Dalio Power Pillars:")
            print_pillars()
        elif command in ["quit", "exit"]:
            print("Exiting simulation.")
            break
        else:
            print("I don't understand that command.")

if __name__ == "__main__":
    main()
