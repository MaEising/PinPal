from dataclasses import dataclass, field

# Für Jeden User muss Jede Strafe als Objekt angelegt werden,
# diese dann in eine Liste joinen und dem PenaltyRecord Objekt übergeben
# generiert automatisch init funktion
@dataclass
class Penalty:
    id: int
    penalty_name: str
    penalty_amount: float
    penalty_quantity: int
    invert: bool

# Ein Penalty Record enthält alle Strafen + Quantity für einen User
# Im Views Endpoint wird dann für jeden User ein PenaltyRecord übergeben
@dataclass
class PenaltyRecord:
    game_id: int
    penalties: list # Liste mit allen Penalty Objekten eines Users
    participant_name: str
    participant_id: int
    avatar_index: int
    participant_total_fine: int = field(default=0)