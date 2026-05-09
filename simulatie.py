from zombie_environment import ZombieEnvironment
from agents.zombie_agent import ZombieAgent
from agents.human_agent import HumanAgent

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
            print(f"Tick {t}: {len(env.humans)} Humans, {len(env.zombies)} Zombies. Avg Trust: {env.stats['avg_trust'][-1]:.2f}")
            
    print("Simulatie voltooid!")
    return env.stats

experiment_data = run_simulation(ticks=50)