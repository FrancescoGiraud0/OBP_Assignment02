> [!Model]
> M/M/n/n/r queue (Engset delay model)

- M -> Markovian components failure rates
- M -> Markovian repairs rates
- n  -> number of components
- n  -> repair queue size
- r  -> number of repairmen

The idea is to compute the probabilities, then assign the state 0 if less than k components are active and state 1 if less (or equal) than k components are active. This way I can determine the fraction of time the system is up. 

#### Unclear points

- [ ] Difference between warm and cold stand-by. (In which case it takes time to setup the new machine?)