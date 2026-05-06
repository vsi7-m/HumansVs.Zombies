import numpy as np
from agents.zombie_agent import ZombieAgent

class ZombieEnvironment:
    """
    De Grid World omgeving voor de Zombie Vs. Humans simulatie.
    """
    def __init__(self, width=30, height=30, seed=42):
        # Breedte en hoogte 30 x 30
        self.width = width
        self.height = height

        self.rng = np.random.default_rng(seed) # numpy random generator van wpo

        self.humans = []
        self.zombies = []

        self.current_warnings = [] # waarschuwingen

        # Statistieken
        self.stats = {
            "ticks": 0,
            "humans_alive": [],
            "zombies_alive": [],
            "new_infections": [],
            "warnings_sent": [],
            "betrayals": [],
            "avg_trust": []
        }

    def add_agent(self, agent, agent_type):
        """Voegt een agent toe aan de simulatie."""
        if agent_type == 'human':
            self.humans.append(agent)
        elif agent_type == 'zombie':
            self.zombies.append(agent)

    def is_valid_position(self, x, y):
        """Controleert of een positie op de grid ligt. Agents mogen niet buiten de grid bewegen."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_nearby_zombies(self, position, radius):
        """Functie om zombies te detecteren."""
        nearby = []
        for zombie in self.zombies:
            distance = max(abs(position[0] - zombie.position[0]), abs(position[1] - zombie.position[1]))
            if distance <= radius:
                nearby.append(zombie)
        return nearby

    def get_nearby_humans(self, position, radius, exclude_agent=None):
        """Functie om humans te detecteren."""
        nearby = []
        for human in self.humans:
            if human != exclude_agent:
                distance = max(abs(position[0] - human.position[0]), abs(position[1] - human.position[1]))
                if distance <= radius:
                    nearby.append(human)
        return nearby

    def add_warning(self, sender_id, target_position, communication_radius):
        """Slaat een waarschuwing op zodat ontvangers deze kunnen verwerken."""
        self.current_warnings.append({"sender_id": sender_id, "position": target_position, "radius": communication_radius})

    def get_warnings(self, position):
        """Haalt actieve waarschuwingen op voor een specifieke positie."""
        received_warnings = []
        for warning in self.current_warnings:
            distance = max(abs(position[0] - warning["position"][0]), abs(position[1] - warning["position"][1]))
            if distance <= warning["radius"]:
                received_warnings.append(warning)
        return received_warnings

    def step(self):
        """
        Voert één tick van de simulatie. (Sense-Think-Act ipv 7-stappenplan uit onze analyse)
        """
        self.stats["ticks"] += 1

        # Agents husselen zodat er geen order bias is
        all_agents = self.humans + self.zombies
        self.rng.shuffle(all_agents)

        for agent in all_agents:
            if agent.is_active: 
                agent.step(self) # polymorfismeeeeee 
        
        self.record_statistics()
        self.current_warnings.clear()

    def record_statistics(self):
        """
        Berekent en bewaart de statistieken van de huidige tick voor latere analyse.
        """
        self.stats["humans_alive"].append(len(self.humans))
        self.stats["zombies_alive"].append(len(self.zombies))
        self.stats["warnings_sent"].append(len(self.current_warnings))

        total_trust = 0
        trust_links = 0
        for h in self.humans:
            for t_val in h.trust.values():
                total_trust += t_val
                trust_links += 1
                
        avg_trust = total_trust / trust_links if trust_links > 0 else 0
        self.stats["avg_trust"].append(avg_trust)

    def convert_to_zombie(self, human):
        """
        Zet een HumanAgent om in een ZombieAgent na een succesvolle infectie.
        """
        if human in self.humans:
            self.humans.remove(human)
            
            new_zombie = ZombieAgent(
                agent_id=f"z_{human.id}", # ID aangepast zodat we weten welke human dit was
                start_position=human.position,
                speed=human.speed
            )
            
            self.zombies.append(new_zombie)

