"""Agent DNA - Genetic Algorithm Evolution"""
import logging
import random
from typing import Dict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class AgentDNA:
    """Genetic code for agent behavior"""
    genes: Dict[str, float] = field(default_factory=lambda: {
        'aggressiveness': random.uniform(0, 1),
        'posting_frequency': random.uniform(0, 1),
        'content_length': random.uniform(0, 1),
        'emoji_usage': random.uniform(0, 1),
        'formality': random.uniform(0, 1),
        'risk_tolerance': random.uniform(0, 1),
        'exploration_rate': random.uniform(0, 1),
        'patience': random.uniform(0, 1)
    })

    def crossover(self, other: 'AgentDNA', mutation_rate: float = 0.1) -> 'AgentDNA':
        """Create child DNA from two parents with mutation"""
        child = AgentDNA()
        for gene_name in self.genes.keys():
            # Inherit from parents (50/50)
            if random.random() < 0.5:
                child.genes[gene_name] = self.genes[gene_name]
            else:
                child.genes[gene_name] = other.genes[gene_name]

            # Mutate?
            if random.random() < mutation_rate:
                child.genes[gene_name] = random.uniform(0, 1)
                logger.debug(f"Mutation in {gene_name}: {child.genes[gene_name]:.2f}")

        return child

    def express_traits(self) -> Dict:
        """Convert genes to behavior parameters"""
        return {
            'max_actions_per_day': int(self.genes['posting_frequency'] * 50 + 10),
            'min_roi_threshold': 1.0 + self.genes['risk_tolerance'] * 2.0,
            'exploration_rate': self.genes['exploration_rate'] * 0.3,
            'average_content_words': int(self.genes['content_length'] * 200 + 50),
            'emoji_per_message': int(self.genes['emoji_usage'] * 5),
            'formality_score': self.genes['formality'],
            'patience_days': int(self.genes['patience'] * 14 + 3)
        }

class GeneticEvolution:
    """Natural selection for agent colony"""

    def __init__(self):
        self.generation = 0
        self.gene_pool: Dict[str, AgentDNA] = {}

    def reproduce(self, parent_a_id: str, parent_b_id: str = None) -> AgentDNA:
        """Create child agent DNA"""
        parent_a_dna = self.gene_pool.get(parent_a_id, AgentDNA())

        if parent_b_id and parent_b_id in self.gene_pool:
            parent_b_dna = self.gene_pool[parent_b_id]
            child_dna = parent_a_dna.crossover(parent_b_dna)
            logger.info(f"Child DNA from {parent_a_id} + {parent_b_id}")
        else:
            # Asexual reproduction with mutation
            child_dna = parent_a_dna.crossover(parent_a_dna, mutation_rate=0.2)
            logger.info(f"Child DNA from {parent_a_id} (asexual)")

        self.generation += 1
        return child_dna

    def register_agent(self, agent_id: str, dna: AgentDNA):
        """Add agent to gene pool"""
        self.gene_pool[agent_id] = dna
