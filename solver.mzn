
int: num_Nodes;
int: num_Edges;
int: num_Agents;
int: max_time ;

array[1..num_Edges] of set of int: edges;
array[1..num_Agents] of int: start;
array[1..num_Agents] of int: goal;


array[0..max_time,1..num_Agents] of var 1..num_Nodes: agentAtTimeT;
array[1..num_Nodes*num_Agents] of int: distances;

include "alldifferent.mzn";



constraint forall(t in 0..max_time,a in 1..num_Agents)(
    distances[agentAtTimeT[t,a] + (num_Nodes * (a-1))] <= max_time -t
);

%Makes it so agents cant pass through the same vertice
constraint forall(t in 0..max_time-1, a in 1..num_Agents)(
    forall(a1 in 1..num_Agents)(
        agentAtTimeT[t+1,a] != agentAtTimeT[t,a1]
        \/
        agentAtTimeT[t+1,a] = agentAtTimeT[t,a]
    )
);


%Inicialize last and first state
constraint forall(a in 1..num_Agents) (
      agentAtTimeT[0,a] = start[a]
      /\  
      agentAtTimeT[max_time,a] = goal[a]
);

% agentAtTimeT = [[1,2],[2,1]]
%                   t1  t2 
%means Agent 1 was in node 1 at time 1 and agent 1 was in node 2 at time 2
constraint forall(t in 0..max_time)( 
    all_different([ agentAtTimeT[t,a] | a in 1..num_Agents ])
);

%What makes the agent move only in its edges
constraint forall(t in 0..max_time-1, a in 1..num_Agents)(
      distances[agentAtTimeT[t,a] + (num_Nodes * (a-1))] <= max_time -t
      /\
      (agentAtTimeT[t+1,a] in edges[agentAtTimeT[t,a]]
      \/
      agentAtTimeT[t+1,a] = agentAtTimeT[t,a]
      )
);


solve  satisfy;
output [

    "\(agentAtTimeT)",
];

