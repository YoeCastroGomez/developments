from enum import Enum 

class MovementSource(Enum):  ## herencia of Enum class
    TELEOP="teleop"
    HOLD = "hold"


class Arbiter:
    
    def decide(self,operator_connected : bool)-> MovementSource :
        if operator_connected :
            return MovementSource.TELEOP
        return MovementSource.HOLD
    
    
            
        
        
#################################################### tests #####################################

arbiter = Arbiter()

resultado = arbiter.decide(True)
print(f"El resultado es {resultado.value}")

resultado = arbiter.decide(False)
print(f"El resultado es {resultado.value}")