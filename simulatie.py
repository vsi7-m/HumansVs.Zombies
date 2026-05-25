import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from zombie_environment import ZombieEnvironment
from agents.zombie_agent import ZombieAgent
from agents.human_agent import HumanAgent

# ==========================================
# ALGEMENE CONFIGURATIE & GLOBALE VARIABELEN
# ==========================================

# Definieer de twee omgevingen voor de experimenten
GRID_CONFIGS = [
    {"width": 30,  "height": 30,  "n_humans": 20, "n_zombies": 1, "label": "30x30"},
    {"width": 100, "height": 100, "n_humans": 50, "n_zombies": 2, "label": "100x100"},
]

# Kleurschema's voor de grafieken
KLEUREN_DETECTIE     = ["red",    "darkred"]
KLEUREN_COMMUNICATIE = ["blue",   "darkblue"]
KLEUREN_GROEP        = ["green",  "darkgreen"]
KLEUREN_VERRAAD      = ["orange", "darkorange"]

# =================
# SIMULATIE RUNNER
# =================

def run_simulation(ticks=100, n_humans=20, n_zombies=1, seed=42,
                   zombie_detection_radius=5, human_communication_radius=10,
                   width=30, height=30):
    """
    Runt een volledige, onzichtbare simulatie.
    Wordt gebruikt door de experiment-functies om snel data te genereren.
    """
    env = ZombieEnvironment(width=width, height=height, seed=seed)

    # Voeg humans toe
    for i in range(n_humans):
        start_pos = [env.rng.integers(0, env.width), env.rng.integers(0, env.height)]
        human = HumanAgent(agent_id=f"H{i}", start_position=start_pos, speed=1, communication_radius=human_communication_radius)
        env.add_agent(human, 'human')

    # Voeg zombies toe
    for i in range(n_zombies):
        start_pos = [env.rng.integers(0, env.width), env.rng.integers(0, env.height)]
        zombie = ZombieAgent(agent_id=f"Z{i}", start_position=start_pos, speed=1, detection_radius=zombie_detection_radius)
        env.add_agent(zombie, 'zombie')

    # Draai de simulatieloop
    for t in range(ticks):
        env.step()

    return env.stats

# ===================================
# EXPERIMENTEN & GRAFIEKEN GENEREREN
# ===================================

def experiment_detectieradius():
    """Test de impact van de detectieradius van zombies op de infectiesnelheid."""
    detectieradiussen = [0, 2, 4, 6, 8, 10, 12, 15, 20]
    aantal_runs = 50
    ticks = 100

    plt.figure(figsize=(9, 5))

    for cfg, kleur in zip(GRID_CONFIGS, KLEUREN_DETECTIE):
        print(f"\n  Grid {cfg['label']}:")
        gem_infectiesnelheden = []
        std_infectiesnelheden = []
        for radius in detectieradiussen:
            infectiesnelheden = []
            for seed in range(aantal_runs):
                stats = run_simulation(
                    ticks=ticks, n_humans=cfg["n_humans"], n_zombies=cfg["n_zombies"],
                    seed=seed, zombie_detection_radius=radius,
                    width=cfg["width"], height=cfg["height"]
                )
                infectiesnelheden.append(sum(stats["new_infections"]) / ticks)

            # Bereken het gemiddelde
            gem = np.mean(infectiesnelheden)
            gem_infectiesnelheden.append(gem)

            # Bereken de standaardafwijking
            std = np.std(infectiesnelheden)
            std_infectiesnelheden.append(std)
            print(f"    Radius {radius:2d}: Gemiddelde {gem:.3f} (Spreiding ±{std:.3f})")
        
        # Converteer naar numpy arrays voor makkelijk rekenwerk in de grafiek
        x = np.array(detectieradiussen)
        y = np.array(gem_infectiesnelheden)
        foutmarge = np.array(std_infectiesnelheden)
        
        # Teken de normale lijn
        plt.plot(x, y, marker="o", color=kleur, label=cfg["label"])
        
        # Teken het betrouwbaarheidsinterval
        plt.fill_between(x, y - foutmarge, y + foutmarge, color=kleur, alpha=0.2)

    plt.xlabel("Detectieradius van zombies")
    plt.ylabel("Gemiddeld aantal nieuwe infecties per tick")
    plt.title("Effect van detectieradius op infectiesnelheid")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("grafiek_detectieradius.png", dpi=300)
    print("Grafiek opgeslagen als grafiek_detectieradius.png")
    plt.close()

def experiment_communicatieradius():
    """Test de impact van de communicatieradius van humans op de infectiesnelheid."""
    communicatieradiussen = [0, 2, 4, 6, 8, 10, 12, 15, 20]
    aantal_runs = 50
    ticks = 100

    plt.figure(figsize=(9, 5))

    for cfg, kleur in zip(GRID_CONFIGS, KLEUREN_COMMUNICATIE):
        print(f"\n  Grid {cfg['label']}:")
        gem_infectiesnelheden = []
        for radius in communicatieradiussen:
            infectiesnelheden = []
            std_infectiesnelheden = []
            for seed in range(aantal_runs):
                stats = run_simulation(
                    ticks=ticks, n_humans=cfg["n_humans"], n_zombies=cfg["n_zombies"],
                    seed=seed, human_communication_radius=radius,
                    width=cfg["width"], height=cfg["height"]
                )
                infectiesnelheden.append(sum(stats["new_infections"]) / ticks)
            # Bereken het gemiddelde
            gem = np.mean(infectiesnelheden)
            gem_infectiesnelheden.append(gem)

            # Bereken de standaardafwijking
            std = np.std(infectiesnelheden)
            std_infectiesnelheden.append(std)
            print(f"    Radius {radius:2d}: {gem:.3f} (±{std:.3f})")

        x = np.array(communicatieradiussen)
        y = np.array(gem_infectiesnelheden)
        marge = np.array(std_infectiesnelheden)

        plt.plot(x, y, marker="o", color=kleur, label=cfg["label"])
        plt.fill_between(x, y - marge, y + marge, color=kleur, alpha=0.2)

    plt.xlabel("Communicatieradius van humans")
    plt.ylabel("Gemiddeld aantal nieuwe infecties per tick")
    plt.title("Effect van communicatieradius op infectiesnelheid")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("grafiek_communicatieradius.png", dpi=300)
    print("Grafiek opgeslagen als grafiek_communicatieradius.png")
    plt.close()

def experiment_groepsvorming_communicatieradius():
    """Test of een grotere communicatieradius leidt tot meer groepsvorming."""
    communicatieradiussen = [0, 2, 4, 6, 8, 10, 12, 15, 20]
    aantal_runs = 50
    ticks = 100

    plt.figure(figsize=(9, 5))

    for cfg, kleur in zip(GRID_CONFIGS, KLEUREN_GROEP):
        print(f"\n  Grid {cfg['label']}:")
        gem_fractions = []
        std_fractions = []
        for radius in communicatieradiussen:
            fractions = []
            for seed in range(aantal_runs):
                stats = run_simulation(
                    ticks=ticks, n_humans=cfg["n_humans"], n_zombies=cfg["n_zombies"],
                    seed=seed, human_communication_radius=radius,
                    width=cfg["width"], height=cfg["height"]
                )
                tick_fractions = [
                    in_group / alive
                    for alive, in_group in zip(stats["humans_alive"], stats["humans_in_group"])
                    if alive > 0
                ]
                if tick_fractions:
                    fractions.append(np.mean(tick_fractions))
            gem = np.mean(fractions) if fractions else 0.0
            std = np.std(fractions) if fractions else 0.0
            gem_fractions.append(gem)
            std_fractions.append(std)
            print(f"    Radius {radius:2d}: {gem:.3f} (±{std:.3f})")

        x = np.array(communicatieradiussen)
        y = np.array(gem_fractions)
        marge = np.array(std_fractions)

        plt.plot(x, y, marker="o", color=kleur, label=cfg["label"])
        plt.fill_between(x, y - marge, y + marge, color=kleur, alpha=0.2)

    plt.xlabel("Communicatieradius van humans")
    plt.ylabel("Gemiddelde aantal humans in GROUPING state")
    plt.title("Effect van communicatieradius op groepsvorming")
    plt.ylim(0, 1) # Groepsvorming is een percentage (0 tot 100%)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("grafiek_groepsvorming_communicatieradius.png", dpi=300)
    print("Grafiek opgeslagen als grafiek_groepsvorming_communicatieradius.png")
    plt.close()

def experiment_verraad_communicatieradius():
    """Test of waarschuwingen het percentage verraad verlaagt."""
    communicatieradiussen = [0, 2, 4, 6, 8, 10, 12, 15, 20]
    aantal_runs = 50
    ticks = 100

    plt.figure(figsize=(9, 5))

    for cfg, kleur in zip(GRID_CONFIGS, KLEUREN_VERRAAD):
        print(f"\n  Grid {cfg['label']}:")
        gem_verraden = []
        std_verraden = []
        for radius in communicatieradiussen:
            verraden_per_run = []
            for seed in range(aantal_runs):
                stats = run_simulation(
                    ticks=ticks, n_humans=cfg["n_humans"], n_zombies=cfg["n_zombies"],
                    seed=seed, human_communication_radius=radius,
                    width=cfg["width"], height=cfg["height"]
                )
                verraden_per_run.append(sum(stats["betrayals"]) / ticks)
            gem = np.mean(verraden_per_run)
            std = np.std(verraden_per_run)
            gem_verraden.append(gem)
            std_verraden.append(std)
            print(f"    Radius {radius:2d}: {gem:.4f} (±{std:.4f})")

        x = np.array(communicatieradiussen)
        y = np.array(gem_verraden)
        marge = np.array(std_verraden)

        plt.plot(x, y, marker="o", color=kleur, label=cfg["label"])
        plt.fill_between(x, y - marge, y + marge, color=kleur, alpha=0.2)

    plt.xlabel("Communicatieradius van humans")
    plt.ylabel("Gemiddeld aantal verraden per tick")
    plt.title("Effect van communicatieradius op verraad")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("grafiek_verraad_communicatieradius.png", dpi=300)
    print("Grafiek opgeslagen als grafiek_verraad_communicatieradius.png")
    plt.close()

# =================
# VISUELE SIMULATIE 
# =================

def run_visual_simulation(ticks=100, n_humans=20, n_zombies=2, seed=42):
    """
    Runt een visuele simulatie met Matplotlib animatie.
    """
    env = ZombieEnvironment(width=30, height=30, seed=seed)

    for i in range(n_humans):
        start_pos = [env.rng.integers(0, env.width), env.rng.integers(0, env.height)]
        human = HumanAgent(agent_id=f"H{i}", start_position=start_pos, speed=1)
        env.add_agent(human, 'human')

    for i in range(n_zombies):
        start_pos = [env.rng.integers(0, env.width), env.rng.integers(0, env.height)]
        zombie = ZombieAgent(agent_id=f"Z{i}", start_position=start_pos, speed=1)
        env.add_agent(zombie, 'zombie')

    fig, ax = plt.subplots(figsize=(10, 8))

    def update(frame):
        env.step()
        ax.clear()
        ax.set_xlim(0, env.width)
        ax.set_ylim(0, env.height)
        ax.set_title(f"Tick {env.stats['ticks']} | Humans: {len(env.humans)} | Zombies: {len(env.zombies)}")
        ax.set_xticks(range(env.width))
        ax.set_yticks(range(env.height))
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        # Teken Zombies
        if env.zombies:
            zx = [z.position[0] for z in env.zombies]
            zy = [z.position[1] for z in env.zombies]
            ax.scatter(zx, zy, color='red', s=80, label='Zombies', zorder=5)

        # Teken Humans + Groepen
        if env.humans:
            hx_wandering, hy_wandering, hx_group, hy_group = [], [], [], []
            for h in env.humans:
                if len(h.group_members) > 0:
                    hx_group.append(h.position[0])
                    hy_group.append(h.position[1])
                else:
                    hx_wandering.append(h.position[0])
                    hy_wandering.append(h.position[1])
            if hx_wandering:
                ax.scatter(hx_wandering, hy_wandering, color='blue', s=60, alpha=0.5, label='Humans (alleen)', zorder=3)
            if hx_group:
                ax.scatter(hx_group, hy_group, color='green', s=60, alpha=0.5, label='Humans (groep)', zorder=3)

        # Teken Waarschuwingen
        if env.current_warnings:
            wx = [w["position"][0] for w in env.current_warnings]
            wy = [w["position"][1] for w in env.current_warnings]
            ax.scatter(wx, wy, color='orange', marker='x', s=120, label='Paniek (Waarschuwing)', zorder=4)

        ax.legend(loc='upper right')

    print("Start visuele simulatie")
    anim = animation.FuncAnimation(fig, update, frames=ticks, interval=200, repeat=False)
    plt.tight_layout()
    plt.show()

# ====
# Main
# ====

if __name__ == "__main__":
    # OPTIE 1: visualisatie
    run_visual_simulation(ticks=100, n_humans=30, n_zombies=2, seed=None)

    # OPTIE 2: geen visualisatie
    #test_data = run_simulation(ticks=100, n_humans=30, n_zombies=2, seed=42)
    #print(test_data["new_infections"])

    # OPTIE 3: experimenten
    #print("EXPERIMENT 1: Detectieradius vs. infectiesnelheid")
    #experiment_detectieradius()

    #print("EXPERIMENT 2: Communicatieradius vs. infectiesnelheid")
    #experiment_communicatieradius()

    #print("EXPERIMENT 3: Communicatieradius vs. groepsvorming")
    #experiment_groepsvorming_communicatieradius()

    #print("EXPERIMENT 4: Communicatieradius vs. verraad")
    #experiment_verraad_communicatieradius()
