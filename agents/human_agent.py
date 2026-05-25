from agents.agent import Agent
from agents.trust_relation import TrustRelation
from enum import Enum

class HumanState(Enum):
    WANDERING = "Wandering"
    GROUPING = "Grouping"
    FLEEING = "Fleeing"

class HumanAgent(Agent):
    """Simuleert een mens in de Zombie Environment."""
    def __init__(self, agent_id, start_position, speed=1, 
                 vision_radius=7, communication_radius=10, grouping_radius=2, 
                 trust_threshold=3, betrayal_probability=0.05, p_zombification=0.90):
        super().__init__(agent_id, start_position, speed)
        
        self.vision_radius = vision_radius
        self.communication_radius = communication_radius
        self.grouping_radius = grouping_radius
        
        self.trust_relations =[]
        self.trust_threshold = trust_threshold
        self.group_members = set()
        self.betrayal_probability = betrayal_probability

        self.infected = False
        self.infection_timer = 0
        self.p_zombification = p_zombification
        
        self.state = HumanState.WANDERING
        self.is_active = True

    def step(self, env):
        """Voert de Sense-Think-Act cyclus uit voor deze specifieke agent."""
        if not self.is_active:
            return
        
       # VERWERK INFECTIE
        if self.infected:
            self.infection_timer -= 1
            if self.infection_timer <= 0:
                if env.rng.random() < self.p_zombification:
                    env.convert_to_zombie(self)
                    return # De human is nu een zombie, beëindig de beurt
                else:
                    self.infected = False # Agent herstelt

        # SENSE
        self.process_warnings(env)
        visible_zombies = env.get_nearby_zombies(self.position, self.vision_radius)
        nearby_humans = env.get_nearby_humans(self.position, self.grouping_radius, exclude_agent=self)
        
        # THINK
        self.update_group_status(nearby_humans)

        if visible_zombies or self.has_received_warnings(env):
            self.state = HumanState.FLEEING
        elif self.group_members:
            self.state = HumanState.GROUPING
        else:
            self.state = HumanState.WANDERING

        # ACT
        if self.state == HumanState.FLEEING:
            # Waarschuw anderen als je ZELF een zombie ziet
            if visible_zombies:
                env.add_warning(self.id, self.position, self.communication_radius)
            self.flee_or_betray(visible_zombies, nearby_humans, env)
            
        elif self.state == HumanState.GROUPING:
            self.move_to_group_center(env)
            
        elif self.state == HumanState.WANDERING:
            if len(nearby_humans) == 1:
                self.move_towards(nearby_humans[0].position, env)
            else:
                self.random_move(env)

    # =========================================
    # HULPFUNCTIES VOOR SOCIAAL GEDRAG & TRUST
    # =========================================

    def get_trust_relation(self, target_id):
        """Zoekt of maakt een vertrouwensband met een andere agent."""
        for relation in self.trust_relations:
            if relation.target_id == target_id:
                return relation

        new_relation = TrustRelation(target_id)
        self.trust_relations.append(new_relation)
        return new_relation

    def process_warnings(self, env):
        """Verhoogt het vertrouwen in agents die waarschuwingen sturen."""
        warnings = env.get_warnings(self.position)
        for w in warnings:
            sender_id = w["sender_id"]
            if sender_id != self.id:
                relation = self.get_trust_relation(sender_id)
                relation.increase()

    def update_group_status(self, nearby_humans):
        """Bepaalt of de agent zich veilig genoeg voelt om een groep te vormen."""
        self.group_members.clear()
        
        # Regel 1: 2 andere humans dichtbij = echte groep (samen met zichzelf zijn dat er 3)
        if len(nearby_humans) >= 2:
            self.group_members.update(nearby_humans)
        
        # Regel 2: 1 vertrouwde human dichtbij = vertrouwd duo, telt ook als groep
        elif len(nearby_humans) == 1:
            other_human = nearby_humans[0]
            relation = self.get_trust_relation(other_human.id)
            if relation.is_trusted(self.trust_threshold):
                self.group_members.add(other_human)

    def has_received_warnings(self, env):
        """Controleert of er waarschuwingen zijn."""
        return len(env.get_warnings(self.position)) > 0
    
    # ========================================
    # HULPFUNCTIES VOOR BEWEGING & OVERLEVING
    # ========================================

    def flee_or_betray(self, visible_zombies, nearby_humans, env):
        """Vlucht voor het gevaar of verraad een ander tijdens paniek om zelf te overleven."""
        flee_from_position = None
        zombie_is_close = len(visible_zombies) > 0

        # Bepaal de oorsprong van gevaar
        if zombie_is_close:
            flee_from_position = visible_zombies[0].position
        else:
            warnings = env.get_warnings(self.position)
            if warnings:
                flee_from_position = warnings[0]["position"]

        if not flee_from_position:
            return 

        # PANIEK REGEL: VERRAAD
        # Kan alleen als er een zombie dichtbij is en de verrader niet in een groep zit
        if zombie_is_close and not self.group_members:
            for victim in nearby_humans:
                # Slachtoffer mag niet in een groep zitten en mag geen vriend zijn
                if victim.group_members:
                    continue
                
                relation = self.get_trust_relation(victim.id)
                if relation.is_trusted(self.trust_threshold):
                    continue
                
                # Het verraad heeft een kleine kans van slagen
                if env.rng.random() <= self.betrayal_probability:
                    env.new_betrayals_this_tick += 1

                    # Duw slachtoffer en vlucht
                    victim.move_towards(flee_from_position, env)
                    self.move_away_from(flee_from_position, env)
                    return

        self.move_away_from(flee_from_position, env) # Vlucht wanneer verraad niet lukt

    def move_to_group_center(self, env):
        """
        Berekent het centrum van de groep en beweegt daarheen om bij elkaar te blijven.
        """
        total_x = self.position[0]
        total_y = self.position[1]
        
        for member in self.group_members:
            total_x += member.position[0]
            total_y += member.position[1]
            
        total_people = len(self.group_members) + 1
        center_x = int(round(total_x / total_people))
        center_y = int(round(total_y / total_people))
        group_center = [center_x, center_y]
        self.move_towards(group_center, env)
