from enum import Enum 

class MovementSource(Enum):  ## herencia of Enum class
    ESTOP = "estop"
    TELEOP="teleop"
    HOLD = "hold"


class Arbiter:
    
    def decide(self,operator_connected : bool, estop_activated : bool )-> MovementSource :
        if estop_activated    :
            return  MovementSource.ESTOP
        elif operator_connected :
            return MovementSource.TELEOP
        return MovementSource.HOLD
    
    
            
        
        
#################################################### tests #####################################

arbiter = Arbiter()

resultado = arbiter.decide(True,False)
print(f"El resultado es {resultado.value}")

resultado = arbiter.decide(False,False)
print(f"El resultado es {resultado.value}")

## new comment 
