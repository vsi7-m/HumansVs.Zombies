from agents.agent import Agent

class HumanState:
    WANDERING = "Wandering"
    GROUPING = "Grouping"
    FLEEING = "Fleeing"

class HumanAgent(Agent):
    def __init__(self, agent_id, start_position, speed=1, 
                 vision_radius=7, communication_radius=10, grouping_radius=2, 
                 trust_threshold=3, betrayal_probability=0.05, p_zombification=0.90):
        # Initialiseer de basis Agent attributen (id, position, speed)
        super().__init__(agent_id, start_position, speed)
        
        self.vision_radius = vision_radius
        self.communication_radius = communication_radius
        self.grouping_radius = grouping_radius
        
        self.trust = {}
        self.trust_threshold = trust_threshold
        self.group_members = set()
        self.betrayal_probability = betrayal_probability

        self.infected = False
        self.infection_timer = 0
        self.p_zombification = p_zombification
        
        self.state = HumanState.WANDERING
        self.is_active = True

    def step(self, env):
        if not self.is_active:
            return
        
       # VERWERK INFECTIE
        if self.infected:
            self.infection_timer -= 1
            if self.infection_timer <= 0:
                if env.rng.random() < self.p_zombification:
                    env.convert_to_zombie(self)
                    return # De human is nu een zombie
                else:
                    self.infected = False

        # SENSE
        self.process_warnings(env) # Trust update
        visible_zombies = env.get_nearby_zombies(self.position, self.vision_radius)
        nearby_humans = env.get_nearby_humans(self.position, self.grouping_radius, exclude_agent=self)
        
        # THINK
        self.update_group_status(nearby_humans) # Vul self.group_members

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
                closest_zombie = visible_zombies[0]
                env.add_warning(self.id, closest_zombie.position, self.communication_radius)
            self.flee_or_betray(visible_zombies, nearby_humans, env)
            
        elif self.state == HumanState.GROUPING:
            self.move_to_group_center(env)
            
        elif self.state == HumanState.WANDERING:
            if len(nearby_humans) == 1:
                self.move_towards(nearby_humans[0].position, env)
            else:
                self.random_move(env)

    def process_warnings(self, env):
        """Ontvangers verhogen de trust-score van de afzender met 1"""
        warnings = env.get_warnings(self.position)
        for w in warnings:
            sender_id = w["sender_id"]
            if sender_id != self.id:
                # trust[sender_id] += 1
                self.trust[sender_id] = self.trust.get(sender_id, 0) + 1

    def update_group_status(self, nearby_humans):
        """
        Vult de set met groepsleden
        """
        self.group_members.clear()
        # Regel 1: 2 andere humans dichtbij = echte groep (samen met zichzelf zijn dat er 3)
        if len(nearby_humans) >= 2:
            self.group_members.update(nearby_humans)
        # Regel 2: 1 vertrouwde human dichtbij = vertrouwd duo, telt ook als groep
        elif len(nearby_humans) == 1:
            other_human = nearby_humans[0]
            if self.trust.get(other_human.id, 0) >= self.trust_threshold:
                self.group_members.add(other_human)

    def has_received_warnings(self, env):
        """Controleert of er waarschuwingen zijn binnengekomen in de observeren fase."""
        return len(env.get_warnings(self.position)) > 0

    def flee_or_betray(self, visible_zombies, nearby_humans, env):
        """
        Vlucht weg van het gevaar, of verraad een ander tijdens paniek om zelf te overleven.
        """
        flee_from_position = None
        zombie_is_close = len(visible_zombies) > 0

        if zombie_is_close:
            closest_zombie = visible_zombies[0]
            flee_from_position = closest_zombie.position
        else:
            # Als er geen zombie is, vluchten we weg van een ontvangen waarschuwing
            warnings = env.get_warnings(self.position)
            if warnings:
                flee_from_position = warnings[0]["position"]

        if not flee_from_position:
            return  # Geen gevaar gevonden, doe niets

        # PANIEK REGEL: VERRAAD
        # Kan alleen als er een zombie dichtbij is en de verrader niet in een groep zit
        if zombie_is_close and not self.group_members:

            for victim in nearby_humans:
                # Het slachtoffer mag ook niet in een groep zitten
                if victim.group_members:
                    continue
                
                # Verraad kan niet als er voldoende vertrouwen is
                if self.trust.get(victim.id, 0) >= self.trust_threshold:
                    continue
                
                # Een kleine random kans moet slagen
                if env.rng.random() <= self.betrayal_probability:
                    
                    # VERRAAD SLAAGT!
                    # Slachtoffer wordt fysiek richting de zombie geduwd
                    victim.move_towards(flee_from_position, env)
                    self.move_away_from(flee_from_position, env)
                    
                    return # Actie is uitgevoerd, stop met zoeken naar slachtoffers

        self.move_away_from(flee_from_position, env) # vluchten wanneer verraad niet lukt

    def move_to_group_center(self, env):
        """
        Berekent het centrum van de groep en beweegt daarheen om bij elkaar te blijven.
        """
        total_x = self.position[0]
        total_y = self.position[1]
        
        # Tel de coördinaten van alle andere groepsleden bij de eigen coördinaten.
        for member in self.group_members:
            total_x += member.position[0]
            total_y += member.position[1]
            
        total_people = len(self.group_members) + 1
        center_x = int(round(total_x / total_people))
        center_y = int(round(total_y / total_people))
        group_center = [center_x, center_y]
        self.move_towards(group_center, env)

    def process_infection(self, env):
        """
        Beheert het infectieproces.
        """
        if self.infected:
            self.infection_timer -= 1
            
            if self.infection_timer <= 0:
                if env.rng.random() < self.p_zombification:
                    env.convert_to_zombie(self)
                else:
                    self.infected = False