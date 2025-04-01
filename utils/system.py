import math
import random as rand

class System:
    # We can model the system as a Engset Delay Model
    # M/M/s/n/n where s is the number of machines and n
    # the number of repairmen
    def __init__(self, n, k, num_repairmen,
                 failure_rate, repair_rate, cold_standby=False):
        self.n = n
        self.k = k
        self.num_repairmen = num_repairmen
        self.lambda_val = failure_rate
        self.mu = repair_rate
        self.cold_standby = cold_standby
    
    def __dist_cold_standby__(self):
        return 
    
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
    
    def sim(self, cycles=10000, warmup_cycles=1000, seed=42):
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
        
    def stationary_distribution(self):
        # Compute stationary distribution
        if self.cold_standby:
            return self.__dist_cold_standby__()
        else:
            return self.__dist_warm_standby__()
        
    def active_time_fraction(self):
        # Considering the system active when only a
        return sum([p_i for i, p_i in enumerate(self.stationary_distribution()) if i<=self.n-self.k])


if __name__ == "__main__":
    sys = System(n=5, k=3, num_repairmen=2, 
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

    print(f"\nActive time fraction (sys.sim(cycles=100000, warmup_cycles=0)): {sys.sim(cycles=1000000):.4f}")
