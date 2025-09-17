from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


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
    complementary_reasons: List[str]
    clippings: List[Clipping]
    massacre: bool
    police_unit: Optional[str]


@dataclass
class Victim:
    id: str
    occurrence_id: str
    type: str
    situation: str
    circumstances: List[str]
    death_date: datetime
    person_type: str
    age: int
    age_group: VictimQualifier
    genre: VictimQualifier
    race: Optional[str]
    place: VictimQualifier
    service_status: VictimQualifier
    qualifications: List[str]
    political_position: PoliticalStatus
    political_status: PoliticalStatus
    partie: Optional[str]
    coorporation: Corporation
    agent_position: Optional[str]
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
    sub_neighborhood: Optional[str]
    locality: Optional[str]
    latitude: float
    longitude: float
    date: datetime
    police_action: bool
    agent_presence: bool
    related_record: Optional[str]
    context_info: ContextInfo
    transports: List[str]
    victims: List[Victim]
    animal_victims: List[str]
