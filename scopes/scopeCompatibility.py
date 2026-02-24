from scopes.scope_rigol_1054z import rigol_1054z
from scopes.scope_tek_MDO3X import tek_MDO3X
from scopes.scope_rigol_MSO5000 import MSO5000

def getCompatibleClass(scope):
    idn = scope.idn()
    fields = idn.split(",")
    print(fields)
    if fields[1] == "DS1104Z":
        scope = rigol_1054z(scope.ipStr)
        return scope
    if fields[1] == "MSO5204":
        scope = MSO5000(scope.ipStr)
        return scope
    elif fields[1] == "MDO34":
        scope = tek_MDO3X(scope.ipStr)
        return scope
    else:
        return None