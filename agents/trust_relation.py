class TrustRelation:
    """
    Houdt de vertrouwensband en statistieken bij 
    tussen deze agent en één specifieke andere agent.
    """
    def __init__(self, target_id):
        self.target_id = target_id
        self.score = 0

    def increase(self, amount=1):
        """Verhoogt de vertrouwensscore."""
        self.score += amount

    def is_trusted(self, threshold):
        """Controleert of de score de drempelwaarde heeft bereikt."""
        return self.score >= threshold