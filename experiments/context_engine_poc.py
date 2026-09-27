import numpy as np

# =====================================================================
# 1. THE DYNAMIC SYNONYM LAYER (Normalizing the Dimensions)
# =====================================================================
# This maps multiple natural language terms to the exact same geometric coordinate,
# preventing our uncompressed dimension space from fragmenting.
DIMENSION_ALIASES = {
    'role_in_event': 'role_in_event',
    'proposer': 'role_in_event',
    'initiator': 'role_in_event',
    'proposal_subject': 'proposal_subject',
    'technology_suggested': 'proposal_subject',
    'proposal_target': 'proposal_target',
    'target_system': 'proposal_target',
    'tester': 'tester',
    'evaluated_by': 'tester'
}

# =====================================================================
# 2. CORE SYMBOLIC ENGINE (The Static Peg Board)
# =====================================================================
class SymbolicContextEngine:
    def __init__(self):
        # Master registries for absolute indices (The static pegs)
        self.entity_registry = {}
        self.dimension_registry = {}
        self.events = {}
        
    def get_or_create_entity(self, name):
        if name not in self.entity_registry:
            self.entity_registry[name] = len(self.entity_registry)
        return self.entity_registry[name]
        
    def get_or_create_dimension(self, raw_name):
        # Normalize the name using the synonym layer
        normalized_name = DIMENSION_ALIASES.get(raw_name, raw_name)
        if normalized_name not in self.dimension_registry:
            self.dimension_registry[normalized_name] = len(self.dimension_registry)
        return self.dimension_registry[normalized_name]

    def make_one_hot_vector(self, index, total_size):
        vec = np.zeros(total_size)
        vec[index] = 1.0
        return vec

    def compute_event_matrix(self, parsed_entities):
        """
        Takes structured entity data and binds them into an exact tensor network.
        No semantic compression occurs.
        """
        N_entities = len(self.entity_registry)
        N_dimensions = len(self.dimension_registry)
        
        # Initialize an empty coordinate space for this specific event
        event_matrix = np.zeros((N_entities, N_dimensions))
        
        for item in parsed_entities:
            entity_name = item['name']
            entity_idx = self.get_or_create_entity(entity_name)
            
            # Regenerate the base one-hot vector for this entity dynamically
            v_entity = self.make_one_hot_vector(entity_idx, N_entities)
            
            for raw_dim, val in item['dimensions'].items():
                dim_idx = self.get_or_create_dimension(raw_dim)
                d_role = self.make_one_hot_vector(dim_idx, N_dimensions)
                
                # If the entity string *value* matches another entity, bind them
                # For basic attributes, we stamp a structural connection weight (1.0)
                fact_matrix = np.outer(v_entity, d_role)
                event_matrix += fact_matrix
                
        return event_matrix

    def query_dimension(self, event_matrix, raw_dimension_name):
        """Uses exact matrix projection to find which entities occupy a dimension"""
        dim_idx = self.dimension_registry.get(DIMENSION_ALIASES.get(raw_dimension_name, raw_dimension_name))
        if dim_idx is None:
            return []
            
        N_dimensions = len(self.dimension_registry)
        query_vec = self.make_one_hot_vector(dim_idx, N_dimensions)
        
        # Project the event matrix against the dimension axis
        projection = np.dot(event_matrix, query_vec)
        
        results = []
        for name, idx in self.entity_registry.items():
            if idx < len(projection) and projection[idx] > 0:
                results.append((name, projection[idx]))
        return results

# =====================================================================
# 3. RUNNING THE PROOF-OF-CONCEPT SIMULATION
# =====================================================================
if __name__ == "__main__":
    engine = SymbolicContextEngine()
    
    # --- STEP A: Prime the registries with our known symbols ---
    # (In production, this updates dynamically as text streams in)
    engine.get_or_create_entity('Alice')
    engine.get_or_create_entity('PostgreSQL')
    engine.get_or_create_entity('payments platform')
    engine.get_or_create_entity('Bob')
    
    engine.get_or_create_dimension('initiator')
    engine.get_or_create_dimension('proposal_subject')
    engine.get_or_create_dimension('proposal_target')
    
    # --- STEP B: Process Event 0 ---
    # "Alice proposed PostgreSQL for the payments platform."
    payload_event0 = [
        {"name": "Alice", "dimensions": {"initiator": "proposed"}},
        {"name": "PostgreSQL", "dimensions": {"proposal_subject": "proposed option"}},
        {"name": "payments platform", "dimensions": {"proposal_target": "target system"}}
    ]
    
    print("Processing Event 0...")
    matrix_e0 = engine.compute_event_matrix(payload_event0)
    
    # --- STEP C: Exact Structural Querying ---
    print("\n--- Running Engine Query ---")
    # Even though we query using the synonym "role_in_event", it resolves perfectly
    proposers = engine.query_dimension(matrix_e0, 'role_in_event')
    print(f"Entities bound to 'role_in_event' in Event 0: {proposers}")
    
    # --- STEP D: Simulating Explicit Ambiguity (Superposition) ---
    # Context: "They approved the database change." (They = 50% Alice, 50% Bob)
    print("\nProcessing Ambiguous Context...")
    N_ent = len(engine.entity_registry)
    N_dim = len(engine.dimension_registry)
    
    # Create an exact split-coordinate vector for the ambiguous identity
    v_they = np.zeros(N_ent)
    v_they[engine.entity_registry['Alice']] = 0.5
    v_they[engine.entity_registry['Bob']] = 0.5
    
    d_approver = engine.make_one_hot_vector(engine.get_or_create_dimension('initiator'), N_dim)
    
    # Outer product spreads the weight perfectly across both coordinates without losing symbol identities
    ambiguous_event = np.outer(v_they, d_approver)
    
    print("\n--- Ambiguous Event Matrix Shape (Entities x Dimensions) ---")
    print(ambiguous_event)
    
    # Querying the ambiguous state
    approvers = engine.query_dimension(ambiguous_event, 'role_in_event')
    print(f"\nQuery Result for Ambiguous Identity: {approvers}")
    print("Notice how the engine outputs both entities with their precise uncertainty weights.")
