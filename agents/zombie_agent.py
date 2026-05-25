from agents.agent import Agent
from enum import Enum

class ZombieState(Enum):
    WANDERING = "Wandering"
    CHASING = "Chasing"
    INFECTING = "Infecting"

class ZombieAgent(Agent):
    """Simuleert een zombie in de Zombie Environment."""
    def __init__(self, agent_id, start_position, speed=1, detection_radius=5, infection_radius=1):
        super().__init__(agent_id, start_position, speed)
        
        self.detection_radius = detection_radius
        self.infection_radius = infection_radius

        self.state = ZombieState.WANDERING
        self.is_active = True

    def step(self, env):
        """Voert de Sense-Think-Act cyclus uit voor deze zombie."""
        if not self.is_active:
            return
        
        # SENSE
        humans_to_infect = env.get_nearby_humans(self.position, self.infection_radius)
        humans_to_chase = env.get_nearby_humans(self.position, self.detection_radius)

        # THINK
        if humans_to_infect:
            self.state = ZombieState.INFECTING
            target_human = env.rng.choice(humans_to_infect)
        elif humans_to_chase:
            self.state = ZombieState.CHASING
            target_human = humans_to_chase[0] 
        else:
            self.state = ZombieState.WANDERING
            target_human = None

        # ACT
        if self.state == ZombieState.INFECTING:
            if not target_human.infected:
                target_human.infected = True
                target_human.infection_timer = env.rng.integers(2, 5) # timer wordt random ingesteld op 2 tot 4 ticks
                env.new_infections_this_tick += 1
        elif self.state == ZombieState.CHASING:
            self.move_towards(target_human.position, env)
        elif self.state == ZombieState.WANDERING:
            self.random_move(env)
        
    