import math
import random as rand

class System:

    def __init__(self, n, k, num_repairmen,
                 failure_rate, repair_rate, cold_standby=False):
        self.n = n
        self.k = k
        self.num_repairmen = num_repairmen
        self.lambda_val = failure_rate
        self.mu = repair_rate
        self.cold_standby = cold_standby

    def __dist_cold_standby__(self):
        """
        Calculate the stationary distribution for the cold standby model using a queue.
        
        In this model:
        - Only `k` components are active at a time and can fail.
        - Failure rate at state j (for j ≤ k): (k - j) * lambda
        - Failure rate at state j (for j > k): 0 -> The system is not active
        - Repair rate at state j: min(j, num_repairmen) * mu
        
        Returns:
        list: List of stationary probabilities π(0) to π(n)
        """
        n = self.n  # Total number of components
        k = self.k  # Number of active components
        s = self.num_repairmen
        lambda_val = self.lambda_val
        mu = self.mu
        
        # Initialize probability queue
        pi = [0] * (n + 1)
        
        # Base case: π(0)
        pi[0] = 1  # Normalization factor will be applied later
        
        # Compute π(j) recursively using balance equations
        for j in range(1, n + 1):
            if j <= n-k+1:
                lambda_j = k * lambda_val  # Failure rate at state j-1
            else:
                lambda_j = 0 # Constant failure rate for j > k
            
            mu_j = min(j, s) * mu  # Repair rate at state j
            
            pi[j] = pi[j - 1] * (lambda_j / mu_j)
        
        # Normalize probabilities so that they sum to 1
        pi_sum = sum(pi)
        pi = [p / pi_sum for p in pi]
        
        return list(pi)

    
    def __dist_warm_standby__(self):
        """
        Calculate the stationary distribution for warm standby model
        
        In this model:
        - n is the total number of states (0 to n)
        - num_repairmen (s) is the threshold parameter for repair capacity
        - failure_rate (lambda) is the forward transition rate
        - repair_rate (mu) is the backward transition rate
        
        Returns:
        list: List of stationary probabilities π(0) to π(n)
        """
        n = self.n
        s = self.num_repairmen
        lambda_val = self.lambda_val
        mu = self.mu
        
        # Calculate lambda/mu ratio once to avoid repeated division
        lambda_mu_ratio = lambda_val / mu
        
        # Calculate pi(0)^(-1)
        pi_0_inverse = 0
        
        # First sum for j ≤ s
        for j in range(s + 1):
            pi_0_inverse += math.comb(n, j) * (lambda_mu_ratio ** j)
        
        # Precompute factorial values we'll need repeatedly
        n_factorial = math.factorial(n)
        s_factorial = math.factorial(s)
        
        # Second sum for j > s
        for j in range(s + 1, n + 1):
            denominator = math.factorial(n - j) * s_factorial * (s ** (j - s))
            pi_0_inverse += (n_factorial / denominator) * (lambda_mu_ratio ** j)
        
        # Calculate π(0)
        pi_0 = 1 / pi_0_inverse
        
        # Initialize list for all probabilities
        pi = [0] * (n + 1)
        pi[0] = pi_0
        
        # Calculate π(j) for j ≤ s
        for j in range(1, s + 1):
            pi[j] = math.comb(n, j) * (lambda_mu_ratio ** j) * pi_0
        
        # Calculate π(j) for j > s
        for j in range(s + 1, n + 1):
            denominator = math.factorial(n - j) * s_factorial * (s ** (j - s))
            pi[j] = (n_factorial / denominator) * (lambda_mu_ratio ** j) * pi_0
        
        return pi
    
    def __sim_cold_standby__(self, cycles=10000, warmup_cycles=1000, seed=42):
        """
        Simulate a k-out-of-n system with cold standby components.
        
        In cold standby:
        - Only k components are active at any time
        - Only active components can fail
        - When an active component fails, a standby component is activated if available
        - Failed components are repaired by available repairmen
        - System is not active (no failures can occur) when j ≥ n-k+1 components have failed
        
        Parameters:
        - cycles: Number of simulation cycles
        - warmup_cycles: Number of initial cycles to exclude from statistics
        - seed: Random seed for reproducibility
        
        Returns:
        - Fraction of time the system is operational
        """
        # Function for generating random exponential lifetimes/repair times
        rand_exp = lambda mu: -math.log(rand.random()) / mu

        # Random seed for replication
        rand.seed(seed)
        
        # Track component states: 0=failed, 1=active, 2=standby
        components_state = [1 if i < self.k else 2 for i in range(self.n)]
        
        # Number of failed components
        num_failed = 0
        
        # Remaining lifetime vector (only for active components)
        lifetimes = [rand_exp(self.lambda_val) if components_state[i] == 1 else float('inf') 
                    for i in range(self.n)]
        
        # Track which components are being repaired and their remaining repair times
        in_repair = {}  # {component_idx: remaining_repair_time}
        # Queue for failed components waiting for repair
        repair_queue = []
        
        system_state = {'t': [], 'state': [], 'comp': [], 'queue_length': [], 'waiting_time': []}
        
        current_time = 0
        total_waiting_time = 0
        num_repairs = 0
        
        for c in range(cycles + warmup_cycles):
            # Determine if system is active (can have failures)
            is_active = num_failed < (self.n - self.k + 1)
            
            # Collect all event times (only failures if system is active)
            event_times = []
            if is_active:
                event_times = [(i, t, "failure") for i, t in enumerate(lifetimes) 
                            if components_state[i] == 1 and t < float('inf')]
            event_times.extend([(i, t, "repair") for i, t in in_repair.items()])
            
            # If no events, break the loop
            if not event_times:
                break
                
            # Find the next event
            event_idx, dt, event_type = min(event_times, key=lambda x: x[1])
            
            # Update current time
            current_time += dt
            
            # Update all timers
            if is_active:
                lifetimes = [max(0, l - dt) if components_state[i] == 1 else l 
                            for i, l in enumerate(lifetimes)]
            in_repair = {i: max(0, t - dt) for i, t in in_repair.items()}
            
            # Determine system state before the event (operational if at least k components are working)
            sys_state = 1 if (self.n - num_failed) >= self.k else 0
            
            # Record state if after warmup
            if c >= warmup_cycles:
                system_state['t'].append(dt)
                system_state['state'].append(sys_state)
                system_state['comp'].append(components_state.copy())
                system_state['queue_length'].append(len(repair_queue))
                
                # Calculate average waiting time so far
                avg_wait = total_waiting_time / max(1, num_repairs)
                system_state['waiting_time'].append(avg_wait)
            
            # Handle the event
            if event_type == "failure":
                # Component failed
                components_state[event_idx] = 0
                num_failed += 1
                
                # Activate a standby component if available and system is still active
                if is_active and num_failed < (self.n - self.k + 1):
                    standby_components = [i for i, state in enumerate(components_state) if state == 2]
                    if standby_components:
                        # Activate the first standby component
                        standby_idx = standby_components[0]
                        components_state[standby_idx] = 1
                        # Set a new lifetime for the newly activated component
                        lifetimes[standby_idx] = rand_exp(self.lambda_val)
                
                # Check if we can start repair immediately
                if len(in_repair) < self.num_repairmen:
                    # Start repair immediately
                    repair_time = rand_exp(self.mu)
                    in_repair[event_idx] = repair_time
                    waiting_time = 0
                else:
                    # Add to repair queue
                    repair_queue.append(event_idx)
                    waiting_time = 0  # Initial waiting time, will be updated when repair starts
                
                # Update stats
                total_waiting_time += waiting_time
                num_repairs += 1
                
            elif event_type == "repair":
                # Component repair completed
                components_state[event_idx] = 2  # Repaired components go to standby
                num_failed -= 1
                
                # If we're below k active components, activate this one
                active_count = sum(1 for state in components_state if state == 1)
                if active_count < self.k:
                    components_state[event_idx] = 1
                    lifetimes[event_idx] = rand_exp(self.lambda_val)
                
                # Remove from in_repair
                del in_repair[event_idx]
                
                # If there are components waiting, start repairing one
                if repair_queue:
                    next_component = repair_queue.pop(0)
                    repair_time = rand_exp(self.mu)
                    in_repair[next_component] = repair_time
                    
                    # Update waiting time for this component
                    waiting_time = current_time - (current_time - dt)  # Simplified
                    total_waiting_time += waiting_time
        
        # Calculate results only from the recorded states (after warmup)
        tot_time = sum(system_state['t'])
        if tot_time == 0:
            return 0
            
        # Fraction of time system was operational
        operational_time = sum(t for t, s in zip(system_state['t'], system_state['state']) if s == 1)
        return operational_time / tot_time
    
    def __sim_warm_standby__(self, cycles=10000, warmup_cycles=1000, seed=42):
        # Function for generating random exponential lifetimes
        rand_exp = lambda mu: -math.log(rand.random()) / mu

        # Random seed for replication
        rand.seed(seed)
        
        # Remaining lifetime vector
        lifetimes = [rand_exp(self.lambda_val) for _ in range(self.n)]
        # State vector (1 = working, 0 = failed)
        components_state = [1]*self.n
        
        # Track which components are being repaired and their remaining repair times
        in_repair = {}  # {component_idx: remaining_repair_time}
        # Queue for failed components waiting for repair
        repair_queue = []
        
        system_state = {'t':[], 'state':[], 'comp':[], 'queue_length':[], 'waiting_time':[]}
        
        current_time = 0
        total_waiting_time = 0
        num_repairs = 0
        
        for c in range(cycles+1):
            # Collect all event times (failures and repair completions)
            event_times = [(i, t, "failure") for i, t in enumerate(lifetimes) if components_state[i] == 1]
            event_times.extend([(i, t, "repair") for i, t in in_repair.items()])
            
            # If no events, break the loop
            if not event_times:
                break
                
            # Find the next event
            event_idx, dt, event_type = min(event_times, key=lambda x: x[1])
            
            # Update current time
            current_time += dt
            
            # Update all timers
            lifetimes = [max(0, l-dt) if components_state[i] == 1 else l for i, l in enumerate(lifetimes)]
            in_repair = {i: max(0, t-dt) for i, t in in_repair.items()}
            
            # Determine system state before the event
            sys_state = 1 if sum(components_state) >= self.k else 0
            
            # Record state if after warmup
            if c > warmup_cycles:
                system_state['t'].append(dt)
                system_state['state'].append(sys_state)
                system_state['comp'].append(components_state.copy())
                system_state['queue_length'].append(len(repair_queue))
                
                # Calculate average waiting time so far
                avg_wait = total_waiting_time / max(1, num_repairs)
                system_state['waiting_time'].append(avg_wait)
            
            # Handle the event
            if event_type == "failure":
                # Component failed
                components_state[event_idx] = 0
                
                # Check if we can start repair immediately
                if len(in_repair) < self.num_repairmen:
                    # Start repair immediately
                    repair_time = rand_exp(self.mu)
                    in_repair[event_idx] = repair_time
                    waiting_time = 0
                else:
                    # Add to repair queue
                    repair_queue.append(event_idx)
                    waiting_time = 0  # Initial waiting time, will be updated when repair starts
                
                # Update stats
                total_waiting_time += waiting_time
                num_repairs += 1
                
            elif event_type == "repair":
                # Component repair completed
                components_state[event_idx] = 1
                lifetimes[event_idx] = rand_exp(self.lambda_val)
                
                # Remove from in_repair
                del in_repair[event_idx]
                
                # If there are components waiting, start repairing one
                if repair_queue:
                    next_component = repair_queue.pop(0)
                    repair_time = rand_exp(self.mu)
                    in_repair[next_component] = repair_time
                    
                    # Update waiting time for this component
                    # (waiting time is from failure to start of repair)
                    waiting_time = dt  # This is a simplification, actual time would need more tracking
                    total_waiting_time += waiting_time
        
        tot_time = sum(system_state['t'])
        if tot_time == 0:
            return 0, 0, 0, system_state
            
        frac_time = [(t/tot_time)*system_state['state'][i] for i,t in enumerate(system_state['t'])]
        
        #avg_queue_length = sum(ql * t for ql, t in zip(system_state['queue_length'], system_state['t'])) / tot_time
        #avg_waiting_time = sum(system_state['waiting_time']) / len(system_state['waiting_time']) if system_state['waiting_time'] else 0
        
        return sum(frac_time)#, avg_queue_length, avg_waiting_time, system_state
    
    def sim(self, cycles=10000, warmup_cycles=1000, seed=42):
        """
        Simulate a k-out-of-n system based on the cold_standby parameter.

        Parameters:
        - cycles: Number of simulation cycles
        - warmup_cycles: Number of initial cycles to exclude from statistics
        - seed: Random seed for reproducibility

        Returns:
        - Fraction of time the system is operational
        """
        if self.cold_standby:
            return self.__sim_cold_standby__(cycles, warmup_cycles, seed)
        else:
            return self.__sim_warm_standby__(cycles, warmup_cycles, seed)
  
    def stationary_distribution(self):
        # Compute stationary distribution
        if self.cold_standby:
            return self.__dist_cold_standby__()
        else:
            return self.__dist_warm_standby__()
        
    def active_time_fraction(self):
        # Considering the system active when only a
        return sum([p_i for i, p_i in enumerate(self.stationary_distribution()) if i<=self.n-self.k])
    

    """
    ## Cost objective function

    - Cost per component
        - *Cold standby* : $\text{Cost per time} * \text{Uptime time fraction}$
        - *Warm standby* : $\text{Cost per time} * \text{Active components time fraction} * \text{Number of components}$
    - Cost per repairmen : $\text{Cost per time}$
    - Downtime cost: $\text{Cost per time} * (1-\text{Uptime time fraction})$

    $$ R + i\times C_i\times T_{up} + D\times (1-T_{up})$$
    """
    def total_cost(self, n, r, component_cost, repairmen_cost, downtime_cost):

        sys = System(n, self.k, self.num_repairmen, self.mu, self.lambda_val, self.cold_standby)

        availability = sys.active_time_fraction()

        if self.cold_standby:
            C = self.k * component_cost * availability
            R = repairmen_cost * r
            D = downtime_cost * (1-availability)
            return C+R+D, availability
        else:
            C=0
            pi = sys.__dist_warm_standby__()
            for i in range(len(pi)):
                C += (n-i) * pi[i] * component_cost
            R = repairmen_cost  * r
            D = downtime_cost * (1-availability)
            return C+R+D, availability

    def optimize(self, max_n, max_repairmen, component_cost, repairmen_cost, downtime_cost):
        opt_result =  {'components':None, 'repairmen':None, 'availability':None, 'total_cost':None}

        if component_cost is None or repairmen_cost is None or downtime_cost is None:
            return opt_result
        
        lowest_cost = math.inf
        
        for n in range(self.k, max_n + 1):
            for r in range(1, max_repairmen + 1):
                cost, availability = self.total_cost(n, r, component_cost, repairmen_cost, downtime_cost)

                config = {
                        "components": n,
                        "repairmen": r,
                        "availability": availability,
                        "total_cost": cost
                    }

                if cost < lowest_cost:
                    lowest_cost = cost
                    best_config = config.copy()

        return best_config

if __name__ == "__main__":
    sys = System(n=5, k=3, num_repairmen=3, 
                 failure_rate=2.0, repair_rate=3.0,
                 cold_standby=True)
    
    # Get stationary distribution
    distribution = sys.stationary_distribution()
    
    print("Stationary Distribution:")
    for j, prob in enumerate(distribution):
        print(f"π({j}) = {prob:.6f}")

    # Calculate active time fraction
    active_time = sys.active_time_fraction()
    print(f"\nActive time fraction: {active_time:.4f}")

    print(f"\nActive time fraction (sys.sim(cycles=100000, warmup_cycles=0)): {sys.sim(cycles=1000000, warmup_cycles=10000):.4f}\n")
    
    # Try Optimization
    print(f"\nBest configuration: {sys.optimize(10, 5, 20, 20, 50)}")

    sys = System(n=5, k=3, num_repairmen=3,
                 failure_rate=2.0, repair_rate=3.0, 
                 cold_standby=False)
    
    # Get stationary distribution
    distribution = sys.stationary_distribution()
    
    print("Stationary Distribution:")
    for j, prob in enumerate(distribution):
        print(f"π({j}) = {prob:.6f}")

    # Calculate active time fraction
    active_time = sys.active_time_fraction()
    print(f"\nActive time fraction: {active_time:.4f}")

    print(f"\nActive time fraction (sys.sim(cycles=100000, warmup_cycles=0)): {sys.sim(cycles=1000000, warmup_cycles=10000):.4f}\n")


    # Try Optimization
    print(f"\nBest configuration: {sys.optimize(10, 5, 20, 20, 50)}")