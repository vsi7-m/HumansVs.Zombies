from agents.agent import Agent

class ZombieState:
    WANDERING = "Wandering"
    CHASING = "Chasing"
    INFECTING = "Infecting"

class ZombieAgent(Agent):
    def __init__(self, agent_id, start_position, speed=1, detection_radius=5, infection_radius=1):
        super().__init__(agent_id, start_position, speed)
        
        # Specifieke zombie attributen
        self.detection_radius = detection_radius
        self.infection_radius = infection_radius
        self.state = ZombieState.WANDERING
        self.is_active = True

    def step(self, env):
        if not self.is_active:
            return
        
        # SENSE: Verzamel informatie uit de omgeving
        humans_to_infect = env.get_nearby_humans(self.position, self.infection_radius)
        humans_to_chase = env.get_nearby_humans(self.position, self.detection_radius)

        # THINK: Bepaal de nieuwe status op basis van de observaties
        if humans_to_infect:
            self.state = ZombieState.INFECTING
            target_human = env.rng.choice(humans_to_infect)
        elif humans_to_chase:
            self.state = ZombieState.CHASING
            target_human = humans_to_chase[0] 
        else:
            self.state = ZombieState.WANDERING
            target_human = None

        # Voer de actie uit die bij de status hoort
        if self.state == ZombieState.INFECTING:
            self.start_infection(target_human, env)
        elif self.state == ZombieState.CHASING:
            self.move_towards(target_human.position, env)
        elif self.state == ZombieState.WANDERING:
            self.random_move(env)

    def start_infection(self, human, env):
        """Start het vertraagde infectieproces."""
        if not human.infected:
            human.infected = True
            human.infection_timer = env.rng.integers(2, 5) # timer wordt random ingesteld op 2 tot 4 ticks
    