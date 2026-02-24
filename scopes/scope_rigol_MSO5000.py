from scopeBase import oscilloscope
from scopeBase import dataScaler
from scopes.scope_rigol_1054z import rigol_1054z


class MSO5000(rigol_1054z):
    def __init__(self,ipStr):
        rigol_1054z.__init__(self,ipStr)
