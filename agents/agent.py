import numpy as np

class Agent:
    """
    De algemene basisklasse voor alle agents in de simulatie.
    Bevat gedeelde logica voor attributen en basisbewegingen.
    """
    def __init__(self, agent_id, start_position, speed):
        self.id = agent_id
        self.position = list(start_position)  # [x, y]
        self.speed = speed
        self.state = None  # Wordt specifiek ingevuld door Zombie of Human

    def move_towards(self, target_position, env):
        """Berekent de kortste route in 8 richtingen naar een doelwit."""
        dx = 0
        if target_position[0] > self.position[0]: dx = self.speed
        elif target_position[0] < self.position[0]: dx = -self.speed
        
        dy = 0
        if target_position[1] > self.position[1]: dy = self.speed
        elif target_position[1] < self.position[1]: dy = -self.speed
        
        self.attempt_move(dx, dy, env)

    def move_away_from(self, threat_position, env):
        """Berekent de directe route (andere kant op) van een gevaar."""
        dx = 0
        if threat_position[0] > self.position[0]: dx = -self.speed
        elif threat_position[0] < self.position[0]: dx = self.speed
        
        dy = 0
        if threat_position[1] > self.position[1]: dy = -self.speed
        elif threat_position[1] < self.position[1]: dy = self.speed
        
        self.attempt_move(dx, dy, env)

    def random_move(self, env):
        """Kies een willekeurige geldige stap. (wandering)"""
        valid_moves = []
        for dx in range(-self.speed, self.speed + 1):
            for dy in range(-self.speed, self.speed + 1):
                # Blijf niet stilstaan
                if dx == 0 and dy == 0:
                    continue
                    
                new_x = self.position[0] + dx
                new_y = self.position[1] + dy
                
                if env.is_valid_position(new_x, new_y):
                    valid_moves.append([new_x, new_y])
                    
        if valid_moves:
            # We zetten .tolist() erachter omdat env.rng.choice een numpy array teruggeeft
            self.position = env.rng.choice(valid_moves).tolist()

    def attempt_move(self, dx, dy, env):
        """
        Probeert te bewegen in de gekozen richting. 
        Als we tegen een muur botsen, proberen we erlangs te sliden.
        """
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        # Plan A: De directe route is vrij
        if env.is_valid_position(new_x, new_y):
            self.position = [new_x, new_y]
        
        # Plan B: Schuif langs de X-as (bv. ren omhoog/omlaag langs de muur)
        elif env.is_valid_position(self.position[0], new_y):
            self.position = [self.position[0], new_y]
            
        # Plan C: Schuif langs de Y-as (bv. ren links/rechts langs de muur)
        elif env.is_valid_position(new_x, self.position[1]):
            self.position = [new_x, self.position[1]]
            
        # Plan D: Zitten we helemaal vast in een hoekje? Doe een willekeurige stap
        else:
            self.random_move(env)

    def step(self, env):
        """
        De actie die de agent elke tick uitvoert.
        Deze moet door de subklassen worden overschreven.
        """
        raise NotImplementedError("Subklassen moeten de step() methode implementeren")
