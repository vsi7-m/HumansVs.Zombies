import numpy as np

from agents.zombie_agent import ZombieAgent
from agents.trust_relation import TrustRelation
from agents.human_agent import HumanState

class ZombieEnvironment:
    """
    De Grid World omgeving voor de Zombie Vs. Humans simulatie.
    """
    def __init__(self, width=30, height=30, seed=42):
        """Initialiseert een nieuwe simulatie-omgeving."""
        
        self.width = width
        self.height = height
        self.rng = np.random.default_rng(seed)

        # Lijst met actieve agents
        self.humans = []
        self.zombies = []

        self.current_warnings = [] # waarschuwingen van mens tot mens

        # Logboek
        self.stats = {
            "ticks": 0,
            "humans_alive": [],
            "zombies_alive": [],
            "new_infections": [],
            "warnings_sent": [],
            "betrayals": [],
            "humans_in_group": [],
            "avg_trust": []
        }

        # Tellers voor huidige tick
        self.new_infections_this_tick = 0
        self.new_betrayals_this_tick = 0 

    def add_agent(self, agent, agent_type):
        """Voegt een agent toe aan de juiste lijst in de environment."""
        if agent_type == 'human':
            self.humans.append(agent)
        elif agent_type == 'zombie':
            self.zombies.append(agent)

    def is_valid_position(self, x, y):
        """Controleert of een positie op de grid ligt."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_nearby_zombies(self, position, radius):
        """
        Zoekt alle zombies binnen een specifieke radius rondom een positie.
        Gebruikt de Chebyshev-afstand.
        """
        nearby = []
        for zombie in self.zombies:
            distance = max(abs(position[0] - zombie.position[0]), abs(position[1] - zombie.position[1]))
            if distance <= radius:
                nearby.append(zombie)
        return nearby

    def get_nearby_humans(self, position, radius, exclude_agent=None):
        """Zoekt alle humans binnen een specifieke radius rondom een positie."""
        nearby = []
        for human in self.humans:
            if human != exclude_agent:
                distance = max(abs(position[0] - human.position[0]), abs(position[1] - human.position[1]))
                if distance <= radius:
                    nearby.append(human)
        return nearby

    def add_warning(self, sender_id, target_position, communication_radius):
        """Slaat een waarschuwing op zodat ontvangers deze kunnen verwerken. (in de SENSE fase)"""
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
        Beheert het resetten van tijdelijke variabelen en het loggen van data.
        """

        # Maak tijdelijke lijsten en tellers leeg voor de nieuwe beurt
        self.current_warnings.clear()
        self.new_infections_this_tick = 0
        self.new_betrayals_this_tick = 0

        self.stats["ticks"] += 1

        # Agents husselen zodat er geen order bias is
        all_agents = self.humans + self.zombies
        self.rng.shuffle(all_agents)

        for agent in all_agents:
            if agent.is_active: 
                agent.step(self) # polymorfismeeeeee 
        
        self.record_statistics()

    def record_statistics(self):
        """Berekent en bewaart de statistieken van de huidige tick."""
        self.stats["humans_alive"].append(len(self.humans))
        self.stats["zombies_alive"].append(len(self.zombies))
        self.stats["warnings_sent"].append(len(self.current_warnings))
        self.stats["new_infections"].append(self.new_infections_this_tick)
        self.stats["betrayals"].append(self.new_betrayals_this_tick)

        # Bereken actieve groepsvorming
        humans_in_group = sum(1 for h in self.humans if h.state == HumanState.GROUPING)
        self.stats["humans_in_group"].append(humans_in_group)

        # Bereken het gemiddelde vertrouwen
        total_trust = 0
        trust_links = 0
        for h in self.humans:
            for relation in h.trust_relations:
                total_trust += relation.score
                trust_links += 1
                
        avg_trust = total_trust / trust_links if trust_links > 0 else 0
        self.stats["avg_trust"].append(avg_trust)

    def convert_to_zombie(self, human):
        """
        Zet een HumanAgent om in een ZombieAgent.
        Verwijdert de human uit de populatie en voegt een nieuwe zombie toe op dezelfde positie.
        """
        if human in self.humans:
            self.humans.remove(human)
            
            new_zombie = ZombieAgent(
                agent_id=f"z_{human.id}", # ID aangepast zodat we weten welke human dit was
                start_position=human.position,
                speed=human.speed
            )
            
            self.zombies.append(new_zombie)
