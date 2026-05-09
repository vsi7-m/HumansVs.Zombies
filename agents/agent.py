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
        """Beweeg in de richting van een specifiek coördinaat."""
        dx = target_position[0] - self.position[0]
        dy = target_position[1] - self.position[1]
        
        # We bepalen de stapgrootte. np.sign geeft -1, 0 of 1, 
        # vermenigvuldigd met de snelheid geeft dit de maximale toegestane stap.
        # We gebruiken min() en max() om niet voorbij het doelwit te schieten.
        if dx != 0:
            step_x = int(np.sign(dx) * min(self.speed, abs(dx)))
        else:
            step_x = 0
            
        if dy != 0:
            step_y = int(np.sign(dy) * min(self.speed, abs(dy)))
        else:
            step_y = 0
            
        new_x = self.position[0] + step_x
        new_y = self.position[1] + step_y
        
        if env.is_valid_position(new_x, new_y):
            self.position = [new_x, new_y]

    def move_away_from(self, threat_position, env):
        """Beweegt de agent weg van een coördinaat (zoals een zombie)."""
        # Door self - threat te doen, draaien we de richting om
        dx = self.position[0] - threat_position[0]
        dy = self.position[1] - threat_position[1]
        
        # Exact hetzelfde als bij move_towards
        step_x = int(np.sign(dx) * min(self.speed, abs(dx))) if dx != 0 else 0
        step_y = int(np.sign(dy) * min(self.speed, abs(dy))) if dy != 0 else 0
            
        new_x = self.position[0] + step_x
        new_y = self.position[1] + step_y
        
        if env.is_valid_position(new_x, new_y):
            self.position = [new_x, new_y]

    def random_move(self, env):
        """Kies een willekeurige geldige richting."""
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

    def step(self, env):
        """
        De actie die de agent elke tick uitvoert.
        Deze moet door de subklassen worden overschreven.
        """
        raise NotImplementedError("Subklassen moeten de step() methode implementeren")
