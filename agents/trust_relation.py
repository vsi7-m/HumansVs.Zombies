class TrustRelation:
    """
    Beheert de vertrouwensband tussen de eigenaar van dit object en één andere specifieke human.
    Dit concept wordt gebruikt om te bepalen of agents zich veilig genoeg voelen 
    om een groep te vormen, en of ze de ander wel of niet zullen verraden bij gevaar.
    """
    def __init__(self, target_id):
        self.target_id = target_id
        self.score = 0

    def increase(self, amount=1):
        """
        Verhoogt de vertrouwensscore.
        Dit gebeurt bijvoorbeeld wanneer de agent een nuttige waarschuwing ontvangt van de target.
        """
        self.score += amount

    def is_trusted(self, threshold):
        """Controleert of de score de drempelwaarde heeft bereikt."""
        return self.score >= threshold