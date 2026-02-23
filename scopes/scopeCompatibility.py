from scopes import scope_rigol_1054z

def getCompatibleClass(scope):
    idn = scope.idn()
    fields = idn.split(",")
    #print(fields)
    if fields[1] == "DS1104Z":
        scope = scope_rigol_1054z.rigol_1054z(scope.ipStr)
        return scope
    else:
        return None