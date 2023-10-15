import sys
import subprocess
import tempfile
import os




n_agents = 0
edges = {}
 


def graph_parser(data):
    graph = open(sys.argv[1],"r")
    
    n_nodes = graph.readline()

    graph.readline() #Skip n_edges
    
    data.write("num_Nodes = " +n_nodes[:-1] +";\n")
    data.write("num_Edges = " +n_nodes[:-1] +";\n")
   
    #Edges inicialization
    
    for i in range(1,int(n_nodes[:-1]) + 1):
        edges[i] = []
    data.write("edges = [\n" )
    aux = ""
    
    for line in graph:
        splitted = line.split(" ")
        edges[int(splitted[0])].append(int(splitted[1]))
        edges[int(splitted[1])].append(int(splitted[0]))
 
    
    for key in edges:
        counter = 0
        aux += "{"
        for e in edges[key]:
            counter = 1
            aux += str(e) + ","
        if counter == 1:
            aux = aux[:-1]    
        aux += "},\n"
        
        
    data.write(aux+"];\n" )
    graph.close()
    return n_nodes


def scenario_parser(data):
    agents = open(sys.argv[2],"r",encoding='utf-8-sig')
    n_ag = agents.readline()
    n_ag = n_ag[:-1]
  
   
    data.write("num_Agents = "+ n_ag +";\n")
    agents.readline()
    
    #Start
    start = []
    aux = ""
    data.write("start = [" )
    for i in range(int(n_ag)):
        line = agents.readline()
        splitted = line.split(" ")
        aux += str(int(splitted[1])) + ","  
        start.append(int(splitted[1][:-1]))
    data.write(aux[:-1]+"];\n" )
    agents.readline()
    
    #Goal
    goal = []
    aux = ""
   
    data.write("goal = [" )
    for i in range(int(n_ag)):
        line = agents.readline()
        splitted = line.split(" ")
        aux += str(int(splitted[1])) + ","  
        goal.append(int(splitted[1][:-1]))
  
    data.write(aux[:-1]+"];"+"\n" )
    agents.close()
    return int(n_ag),start,goal

    
def replace_t(t):
    data = open("data.dzn","r+")
    data.seek(0, os.SEEK_END)
    pos = data.tell() - 1
    while pos > 0 and data.read(1) != "\n":
        pos -= 1
        data.seek(pos, os.SEEK_SET)
    data.seek(pos, os.SEEK_SET)
    data.truncate()
    data.write("\nmax_time = "+str(t))
    data.close()




def bfs(edges, node,n_nodes,start): 
    visited = []
    queue = []     
    distance = 0
    distances = {}
    for e in range(1,int(n_nodes)+1):
        distances[e] = -1
    visited.append(node)
    queue.append([node,distance])
    while queue:          
        curr_node, distance = queue.pop(0)
        distances[curr_node] = distance
        for neighbour in edges[curr_node]:
            if neighbour not in visited:
                visited.append(neighbour)
                queue.append([neighbour,distance +1])
    max = distances[start]
    return distances,max
                
          

def main():
    t = 0
    data = open("data.dzn","w")
    n_nodes = graph_parser(data)
    n_agents,start,goal = scenario_parser(data)
    output = ""
    data.write("distances = [" )
    aux = ""
    for i in range(int(n_agents)):
        distance,max_temp = bfs(edges,goal[i],n_nodes,start[i])
        t = max(t,max_temp)
        for i in range(1,int(n_nodes)+1):
            aux += str(distance[i]) + ","
    data.write(aux[:-1])
    data.write("];\n" )
    data.write("max_time = "+str(t))
    data.close()
    with tempfile.TemporaryFile() as tempf:
        
        proc = subprocess.Popen(["minizinc", "--solver", "Chuffed", "solver.mzn", "data.dzn"], stdout=tempf)
        proc.wait()
        tempf.seek(0)
        output = tempf.read()
        
        while(output== b'=====UNSATISFIABLE=====\n'):
            t+=1
            replace_t(t)
            tempf.seek(0)
            tempf.truncate(0)
            proc = subprocess.Popen(["minizinc", "--solver", "Chuffed", "solver.mzn", "data.dzn"], stdout=tempf)
            proc.wait()
            tempf.seek(0)
            output = tempf.read()    
        
        # # test t-1
        # save_out = output
        # replace_t(t-1)
        # tempf.seek(0)
        # tempf.truncate(0)
        # proc = subprocess.Popen(["minizinc", "--solver", "Chuffed", "proj.mzn", "data.dzn"], stdout=tempf)
        # proc.wait()
        # tempf.seek(0)
        # output = tempf.read()
        # if(output == b'=====UNSATISFIABLE=====\n' ):
        #     output = save_out
        # else:
        #     t -= 1
    
    output = output.decode("utf-8")

    list = output.split(",")
    list[0] = list[0][1:]
    list[-1] = list[-1][:-13]
    i= 0
    out = ""
    t = 0
    for i in range(0,len(list),int(n_agents)):
        line = "i=" + str(t) +"\t"
        for e in range(1,int(n_agents)+1):
            if ( i+e-1 ) != 0:
                list[i+e-1] = list[i+e-1][1:]
            line += " " + str(e)+ ":" + str(list[i+e-1])
        t+=1
        out += line + "\n"
    print(out)


if __name__ == "__main__":
    main()