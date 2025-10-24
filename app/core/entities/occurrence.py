from dataclasses import dataclass
from datetime import datetime


@dataclass
class State:
    id: str
    name: str


@dataclass
class Region:
    id: str
    region: str
    state: str
    enabled: bool


@dataclass
class City:
    id: str
    name: str


@dataclass
class Neighborhood:
    id: str
    name: str


@dataclass
class MainReason:
    id: str
    name: str


@dataclass
class Clipping:
    id: str
    name: str


@dataclass
class VictimQualifier:
    id: str
    name: str


@dataclass
class PoliticalStatus:
    id: str
    name: str
    type: str


@dataclass
class Corporation:
    id: str
    name: str


@dataclass
class AgentStatus:
    id: str
    name: str
    type: str


@dataclass
class ContextInfo:
    main_reason: MainReason
    complementary_reasons: list[str]
    clippings: list[Clipping]
    massacre: bool
    police_unit: str | None


@dataclass
class Victim:
    id: str
    occurrence_id: str
    type: str
    situation: str
    circumstances: list[str]
    death_date: datetime
    person_type: str
    age: int
    age_group: VictimQualifier
    genre: VictimQualifier
    race: str | None
    place: VictimQualifier
    service_status: VictimQualifier
    qualifications: list[str]
    political_position: PoliticalStatus
    political_status: PoliticalStatus
    partie: str | None
    coorporation: Corporation
    agent_position: str | None
    agent_status: AgentStatus
    unit: str


@dataclass
class Occurrence:
    id: str
    document_number: int
    address: str
    state: State
    region: Region
    city: City
    neighborhood: Neighborhood
    sub_neighborhood: str | None
    locality: str | None
    latitude: float
    longitude: float
    date: datetime
    police_action: bool
    agent_presence: bool
    related_record: str | None
    context_info: ContextInfo
    transports: list[str]
    victims: list[Victim]
    animal_victims: list[str]
