from zombie_environment import ZombieEnvironment
from agents.zombie_agent import ZombieAgent
from agents.human_agent import HumanAgent

import matplotlib.pyplot as plt
import matplotlib.animation as animation

def run_simulation(ticks=100, n_humans=20, n_zombies=1, seed=42):
    """
    Runt een volledige simulatie van Zombie vs. Humans.
    """
    env = ZombieEnvironment(width=30, height=30, seed=seed)
    
    # Voeg humans toe
    for i in range(n_humans):
        start_pos = [env.rng.integers(0, env.width), env.rng.integers(0, env.height)]
        human = HumanAgent(agent_id=f"H{i}", start_position=start_pos, speed=1)
        env.add_agent(human, 'human')
        
    # Voeg zombies toe
    for i in range(n_zombies):
        start_pos = [env.rng.integers(0, env.width), env.rng.integers(0, env.height)]
        zombie = ZombieAgent(agent_id=f"Z{i}", start_position=start_pos, speed=1)
        env.add_agent(zombie, 'zombie')
        
    # Draai de simulatieloop
    print(f"Start simulatie met {len(env.humans)} humans en {len(env.zombies)} zombies.")
    
    for t in range(ticks):
        env.step()
        
        # Print elke 10 ticks een korte statusupdate
        if t % 10 == 0:
            print(f"Tick {t}: {len(env.humans)} Humans, {len(env.zombies)} Zombies. Avg Trust: {env.stats['avg_trust'][-1]:.2f}, Waarschuwingen: {env.stats['warnings_sent'][-1]}")
            
    print("Simulatie voltooid!")
    return env.stats

def run_visual_simulation(ticks=100, n_humans=20, n_zombies=2, seed=42):
    """
    Runt een visuele simulatie
    """
    # Initialiseer de Omgeving
    env = ZombieEnvironment(width=30, height=30, seed=seed)
    
    # Voeg Humans toe
    for i in range(n_humans):
        start_pos = [env.rng.integers(0, env.width), env.rng.integers(0, env.height)]
        human = HumanAgent(agent_id=f"H{i}", start_position=start_pos, speed=1)
        env.add_agent(human, 'human')
        
    # Voeg Zombies toe
    for i in range(n_zombies):
        start_pos = [env.rng.integers(0, env.width), env.rng.integers(0, env.height)]
        zombie = ZombieAgent(agent_id=f"Z{i}", start_position=start_pos, speed=1)
        env.add_agent(zombie, 'zombie')

    # Setup Matplotlib Figuur 
    fig, ax = plt.subplots(figsize=(10, 8))

    # De Update Functie (Wordt elke tick aangeroepen)
    def update(frame):
        # Voer één tick van de simulatie uit
        env.step()

        # Maak het scherm schoon voor de nieuwe tick
        ax.clear()

        # Teken het grid en stel de limieten in
        ax.set_xlim(0, env.width)
        ax.set_ylim(0, env.height)
        ax.set_title(f"Tick {env.stats['ticks']} | Humans: {len(env.humans)} | Zombies: {len(env.zombies)}")
        
        # We maken een visueel grid 
        ax.set_xticks(range(env.width))
        ax.set_yticks(range(env.height))
        ax.grid(True, linestyle='--', alpha=0.3)

        ax.set_xticklabels([])
        ax.set_yticklabels([])

        # TEKEN ZOMBIES (Rode stippen)
        if env.zombies:
            zx = [z.position[0] for z in env.zombies]
            zy = [z.position[1] for z in env.zombies]
            ax.scatter(zx, zy, color='red', s=80, label='Zombies', zorder=5)

        # TEKEN HUMANS
        if env.humans:
            hx_wandering = []
            hy_wandering = []
            hx_group = []
            hy_group = []

            for h in env.humans:
                # We tekenen mensen in een groep in het GROEN, alleen in het BLAUW
                if len(h.group_members) > 0:
                    hx_group.append(h.position[0])
                    hy_group.append(h.position[1])
                else:
                    hx_wandering.append(h.position[0])
                    hy_wandering.append(h.position[1])

            if hx_wandering:
                ax.scatter(hx_wandering, hy_wandering, color='blue', s=60, label='Humans (alleen)')
            if hx_group:
                ax.scatter(hx_group, hy_group, color='green', s=60, label='Humans (groep)')

        # TEKEN WAARSCHUWINGEN (Oranje kruisjes)
        if env.current_warnings:
            wx = [w["position"][0] for w in env.current_warnings]
            wy = [w["position"][1] for w in env.current_warnings]
            ax.scatter(wx, wy, color='orange', marker='x', s=120, label='Paniek (Waarschuwing)', zorder=4)

        ax.legend(loc='upper right')

    print("Start visuele simulatie")
    # interval=200 betekent 200 milliseconden per tick (dus 5 ticks per seconde)
    anim = animation.FuncAnimation(fig, update, frames=ticks, interval=200, repeat=False)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    # OPTIE 1: visualisatie
    run_visual_simulation(ticks=50, n_humans=30, n_zombies=2, seed=42)

    # OPTIE 2: geen visualisatie
    #experiment_data = run_simulation(ticks=50, n_humans=30, n_zombies=2, seed=42)