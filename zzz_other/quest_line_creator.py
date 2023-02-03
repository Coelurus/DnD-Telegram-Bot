print(" === Questline Tree Creator === ")

tree = input("Input root: ")

def add_vertex(tree):
    tree = tree + "("
    
    print(tree)
    vertex_name = input("Input vertex name on succues: ")
    tree = tree + vertex_name
    if vertex_name != "None":
        tree = add_vertex(tree)
        
    print(tree)
    vertex_name = input("Input vertex name on fail.  : ")
    tree = tree + ";" + vertex_name
    if vertex_name != "None":
        tree = add_vertex(tree)
        
    tree = tree + ")"

    return tree



tree = add_vertex(tree)

print(tree)
input("Press anythin to end...")