# Pokemon-Showdown-Bot
Format: Gen 9 Random Battle

- 6 random Pokemon with random moves
- No choice of lead
- No preview of opponent's team

Assume all user's and opponent's Pokemon have optimum IVs and EVs are spread evenly (85 EVs) for all stats with neutral natures 

Bot1 NoSwitchDamagePlayer :
- Assigns values to damaging moves only, based on hard-coded rules, choose one with highest score
  
Bot2 EvaluateOrderPlayer :
- Evaluates all possible switches, attacks and status moves
- Takes into account moves' properties (expected hits, secondary effects, if breaks protect, crit ratio, if has fixed damage (like seismic toss), switch moves (like u-turn, volt switch), priority, recoil, drain)
- Takes into account user's hp, defenses and speed
- Uses pre-existing file of target's possible moves to better predict if we need to switch
- Takes into account user's and target's boosts and statuses (+ correctly works with ability Guts)
- Other minor heuristics
   
EvaluateOrderPlayer wins SimpleHeuristicsPlayer(built-in bot) 60% of the times 

Possible improvements :
- evaluate terrains (and moves, abilities and items tied to them)
- evaluate entry hazards (e.g. spikes, spiky web) and battle's side conditions (e.g. light screen, reflect)
- evaluate when it is best to terastallize 
